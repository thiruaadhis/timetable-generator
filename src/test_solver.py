import json
import pytest
from solver import main
from load_data import load_data


def run_solver():
    main()
    with open("output/timetable.json") as f:
        return json.load(f)


def test_solver_runs_successfully():
    timetable = run_solver()
    assert timetable is not None
    assert len(timetable) > 0


def test_labs_are_consecutive():
    courses, _, _ = load_data()
    timetable = run_solver()

    lab_courses = set(
        courses[courses["weekly_hours"] == 2]["course_id"]
    )

    for course_id in lab_courses:
        entry = timetable.get(course_id)
        if "periods" in entry:
            periods = entry["periods"]
            assert len(periods) == 2
            p1 = int(periods[0].split()[-1])
            p2 = int(periods[1].split()[-1])
            assert p2 == p1 + 1


def test_lab_not_in_last_period():
    courses, _, _ = load_data()
    timetable = run_solver()

    lab_courses = set(
        courses[courses["weekly_hours"] == 2]["course_id"]
    )

    for course_id in lab_courses:
        entry = timetable.get(course_id)
        if "periods" in entry:
            first_period = int(entry["periods"][0].split()[-1])
            assert first_period != 4  # cannot start in last slot


def test_no_student_conflicts():
    courses, faculty, students = load_data()
    timetable = run_solver()

    for _, student in students.iterrows():
        assigned_slots = []

        for course in student["courses"]:
            if course in timetable:
                entry = timetable[course]

                if "periods" in entry:
                    assigned_slots.extend(
                        (entry["day"], p) for p in entry["periods"]
                    )
                else:
                    assigned_slots.append(
                        (entry["day"], entry["period"])
                    )

        assert len(assigned_slots) == len(set(assigned_slots))


def test_no_faculty_conflicts():
    courses, faculty, _ = load_data()
    timetable = run_solver()

    faculty_map = dict(zip(courses["course_id"], courses["faculty_id"]))

    faculty_schedule = {}

    for course_id, entry in timetable.items():
        faculty_id = faculty_map[course_id]

        if faculty_id not in faculty_schedule:
            faculty_schedule[faculty_id] = []

        if "periods" in entry:
            faculty_schedule[faculty_id].extend(
                (entry["day"], p) for p in entry["periods"]
            )
        else:
            faculty_schedule[faculty_id].append(
                (entry["day"], entry["period"])
            )

    for slots in faculty_schedule.values():
        assert len(slots) == len(set(slots))
