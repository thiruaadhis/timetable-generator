import json
import pytest
from solver import main
from validate import (
    validate_slot_range,
    validate_lab_consecutive,
    validate_no_room_conflicts,
    validate_honours_only_p8,
    validate_mentor_hour_block,
    validate_open_elective_slots,
)


def run_solver():
    main()
    with open("output/timetable.json") as f:
        return json.load(f)


def test_solver_runs():
    timetable = run_solver()
    assert timetable is not None
    assert len(timetable) > 0


def test_slot_ranges_valid():
    timetable = run_solver()
    validate_slot_range(timetable)


def test_lab_consecutive():
    timetable = run_solver()
    validate_lab_consecutive(timetable)


def test_room_conflicts():
    timetable = run_solver()
    validate_no_room_conflicts(timetable)


def test_honours_restriction():
    timetable = run_solver()
    validate_honours_only_p8(timetable)


def test_mentor_hour_blocked():
    timetable = run_solver()
    validate_mentor_hour_block(timetable)


def test_open_elective_lock():
    timetable = run_solver()
    validate_open_elective_slots(timetable)
