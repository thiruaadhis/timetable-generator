from ortools.sat.python import cp_model
from load_data import load_data
import constraints
import json
import os

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS_PER_DAY = 4
TOTAL_SLOTS = len(DAYS) * SLOTS_PER_DAY


def slot_to_time(slot):
    day = DAYS[slot // SLOTS_PER_DAY]
    time = slot % SLOTS_PER_DAY
    return day, f"Period {time+1}"


def main():
    courses, faculty, students = load_data()

    model = cp_model.CpModel()

    # Identify labs (2-period courses)
    lab_courses = set(
        courses[courses["weekly_hours"] == 2]["course_id"]
    )

    # Create decision variables
    course_slots = {
        row["course_id"]: model.NewIntVar(0, TOTAL_SLOTS - 1, row["course_id"])
        for _, row in courses.iterrows()
    }

    # Build conflict graphs (optimized)
    student_conflicts = constraints.build_student_conflict_graph(students)
    faculty_conflicts = constraints.build_faculty_conflict_graph(courses)

    # Merge conflicts
    all_conflicts = student_conflicts.union(faculty_conflicts)

    # Add constraints
    constraints.add_conflict_constraints(
        model,
        course_slots,
        all_conflicts,
        lab_courses
    )

    constraints.add_lab_structure_constraints(
        model,
        course_slots,
        lab_courses,
        SLOTS_PER_DAY
    )

    # Solver settings (performance tuning)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        timetable = {}

        for course_id, var in course_slots.items():
            slot = solver.Value(var)
            day, time = slot_to_time(slot)

            if course_id in lab_courses:
                _, time2 = slot_to_time(slot + 1)
                timetable[course_id] = {
                    "day": day,
                    "periods": [time, time2]
                }
            else:
                timetable[course_id] = {
                    "day": day,
                    "period": time
                }

        os.makedirs("output", exist_ok=True)
        with open("output/timetable.json", "w") as f:
            json.dump(timetable, f, indent=4)

        print("Timetable generated successfully.")

    else:
        print("No feasible solution found.")


if __name__ == "__main__":
    main()
