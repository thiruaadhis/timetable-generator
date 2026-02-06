from ortools.sat.python import cp_model
from load_data import load_data
import constraints
import json
import os
from collections import defaultdict
import timetable_test


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS_PER_DAY = 8
TOTAL_SLOTS = 48


def slot_to_time(slot):
    day = DAYS[slot // SLOTS_PER_DAY]
    period = slot % SLOTS_PER_DAY
    return day, f"Period {period+1}"


def main():
    courses, faculty, students, rooms = load_data()
    model = cp_model.CpModel()

    lab_courses = set(courses[courses["type"] == "lab"]["course_id"])

    course_slots = {}
    room_vars = {}

    for _, row in courses.iterrows():
        cid = row["course_id"]
        hours = row["weekly_hours"]

        if cid in lab_courses:
            start = model.NewIntVar(0, TOTAL_SLOTS - 2, f"{cid}_start")
            course_slots[cid] = [start]

        else:
            course_slots[cid] = [
                model.NewIntVar(0, TOTAL_SLOTS - 1, f"{cid}_{i}")
                for i in range(hours)
            ]
            model.AddAllDifferent(course_slots[cid])

        room_vars[cid] = model.NewIntVar(0, len(rooms) - 1, f"{cid}_room")

    conflicts = constraints.build_conflicts(students, courses)

    constraints.add_conflict_constraints(
        model,
        course_slots,
        conflicts,
        lab_courses
    )

    constraints.add_room_constraints(
        model,
        course_slots,
        room_vars
    )

    constraints.add_fixed_slot_constraints(
        model,
        course_slots,
        courses
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No feasible solution.")
        return

    timetable = defaultdict(dict)

    for cid in course_slots:
        slots = course_slots[cid]
        faculty_name = faculty.loc[
            faculty["faculty_id"] ==
            courses.loc[courses["course_id"] == cid, "faculty_id"].values[0],
            "name"
        ].values[0]

        dept = cid[:3]

        for slot_var in slots:
            slot = solver.Value(slot_var)
            day, period = slot_to_time(slot)

            timetable[dept].setdefault(day, {})
            timetable[dept][day][period] = {
                "course": courses.loc[
                    courses["course_id"] == cid,
                    "name"
                ].values[0],
                "faculty": faculty_name,
                "room": rooms.iloc[
                    solver.Value(room_vars[cid])
                ]["room_id"]
            }

    os.makedirs("output", exist_ok=True)
    with open("output/timetable.json", "w") as f:
        json.dump(timetable, f, indent=4)

    print("Timetable generated.\n")
    timetable_test.render()


if __name__ == "__main__":
    main()
