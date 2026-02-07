from ortools.sat.python import cp_model
from load_data import load_data
import constraints
import json
import os
from collections import defaultdict
import timetable_build


# Time configuration
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS_PER_DAY = 8
TOTAL_SLOTS = 48  # 6 days * 8 periods


def slot_to_time(slot):
    """Convert slot number (0-47) to (day, period)"""
    day = DAYS[slot // SLOTS_PER_DAY]
    period = slot % SLOTS_PER_DAY
    return day, f"Period {period + 1}"


def main():
    print("\n🚀 Starting Timetable Generation...\n")
    
    # Load data
    courses, faculty, students, rooms = load_data()
    print(f"✅ Loaded {len(courses)} courses, {len(faculty)} faculty, {len(students)} students")
    
    # Initialize CP-SAT model
    model = cp_model.CpModel()
    
    # Identify lab courses
    lab_courses = set(courses[courses["type"] == "lab"]["course_id"])
    print(f"✅ Identified {len(lab_courses)} lab courses\n")

    # Decision variables
    course_slots = {}  # Maps course_id to list of slot variables
    room_vars = {}     # Maps course_id to room variable

    # Create slot and room variables for each course
    for _, row in courses.iterrows():
        cid = row["course_id"]
        weekly_hours = row["weekly_hours"]

        if cid in lab_courses:
            # Labs: 2 consecutive periods, store only start slot
            start = model.NewIntVar(0, TOTAL_SLOTS - 2, f"{cid}_start")
            course_slots[cid] = [start]
        else:
            # Regular courses: one slot per weekly hour
            course_slots[cid] = [
                model.NewIntVar(0, TOTAL_SLOTS - 1, f"{cid}_h{i}")
                for i in range(weekly_hours)
            ]
            # All slots for this course must be different
            model.AddAllDifferent(course_slots[cid])

        # Room assignment variable
        room_vars[cid] = model.NewIntVar(0, len(rooms) - 1, f"{cid}_room")

    # Build conflict pairs
    print("🔧 Building constraints...")
    conflicts = constraints.build_conflicts(students, courses)
    print(f"   • {len(conflicts)} conflict pairs identified")

    # Add all constraints
    constraints.add_conflict_constraints(
        model, course_slots, conflicts, lab_courses
    )
    print("   • Student & faculty conflicts added")

    constraints.add_room_constraints(
        model, course_slots, room_vars, TOTAL_SLOTS, len(rooms)
    )
    print("   • Room conflict prevention added")

    constraints.add_fixed_slot_constraints(
        model, course_slots, courses
    )
    print("   • Fixed slot constraints added (Mentor Hour, P8, Open Electives)")

    constraints.add_room_type_constraints(
        model, room_vars, courses, rooms
    )
    print("   • Room type matching added\n")

    # Solve the model
    print("⚙️  Solving with CP-SAT optimizer...")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    # Check solution status
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"\n❌ No solution found!")
        print(f"   Status: {solver.StatusName(status)}")
        print("   Try relaxing some constraints or adding more rooms/time slots.\n")
        return

    print(f"✅ Solution found! (Status: {solver.StatusName(status)})\n")

    # Build timetable from solution
    timetable = defaultdict(dict)

    for cid in course_slots:
        # Get course details
        course_row = courses.loc[courses["course_id"] == cid]
        course_name = course_row["name"].values[0]
        faculty_id = course_row["faculty_id"].values[0]
        faculty_name = faculty.loc[faculty["faculty_id"] == faculty_id, "name"].values[0]
        room_id = rooms.iloc[solver.Value(room_vars[cid])]["room_id"]
        
        # Determine department from course ID (first 3 chars)
        dept = cid[:3]

        # Add all scheduled slots to timetable
        for slot_var in course_slots[cid]:
            slot = solver.Value(slot_var)
            day, period = slot_to_time(slot)

            timetable[dept].setdefault(day, {})
            timetable[dept][day][period] = {
                "course": course_name,
                "faculty": faculty_name,
                "room": room_id
            }

            # If it's a lab, also add the consecutive second period
            if cid in lab_courses:
                next_slot = slot + 1
                next_day, next_period = slot_to_time(next_slot)
                
                timetable[dept].setdefault(next_day, {})
                timetable[dept][next_day][next_period] = {
                    "course": course_name,
                    "faculty": faculty_name,
                    "room": room_id
                }

    # Save to JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "timetable.json")
    with open(output_path, "w") as f:
        json.dump(timetable, f, indent=4)

    print(f"💾 Timetable saved to: {output_path}\n")
    
    # Render beautiful terminal output
    timetable_build.render()


if __name__ == "__main__":
    main()