from ortools.sat.python import cp_model
from load_data import load_data
import constraints
import json

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS_PER_DAY = 4
TOTAL_SLOTS = 20


def slot_to_time(slot):
    day = DAYS[slot // SLOTS_PER_DAY]
    time = slot % SLOTS_PER_DAY
    return day, f"Slot {time+1}"


def main():
    courses, faculty, students = load_data()

    model = cp_model.CpModel()

    course_slots = {}

    # Create one slot variable per course
    for _, row in courses.iterrows():
        course_id = row["course_id"]
        course_slots[course_id] = model.NewIntVar(
            0, TOTAL_SLOTS - 1, course_id
        )

    # Add constraints
    constraints.add_basic_constraints(model, course_slots)
    constraints.add_student_constraints(model, course_slots, students)
    constraints.add_faculty_constraints(model, course_slots, courses, faculty)
    constraints.add_faculty_workload_constraint(model, courses, faculty)
    constraints.add_credit_constraints(students, courses)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        timetable = {}

        for course_id, var in course_slots.items():
            slot = solver.Value(var)
            day, time = slot_to_time(slot)

            timetable[course_id] = {
                "day": day,
                "time": time
            }

            print(f"{course_id} → {day} {time}")

        with open("output/timetable.json", "w") as f:
            json.dump(timetable, f, indent=4)

        print("\nTimetable saved to output/timetable.json")

    else:
        print("No feasible solution found.")


if __name__ == "__main__":
    main()
