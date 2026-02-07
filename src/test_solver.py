import json
import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    """Run the solver and return the generated timetable"""
    main()
    
    # Load the generated timetable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_path = os.path.join(project_root, "output", "timetable.json")
    
    with open(output_path) as f:
        return json.load(f)


def test_solver_runs():
    """Test that the solver runs and produces output"""
    timetable = run_solver()
    assert timetable is not None
    assert len(timetable) > 0


def test_slot_ranges_valid():
    """Test that all slots are valid days and periods"""
    timetable = run_solver()
    validate_slot_range(timetable)


def test_lab_consecutive():
    """Test that labs occupy consecutive periods"""
    timetable = run_solver()
    validate_lab_consecutive(timetable)


def test_room_conflicts():
    """Test that there are no room conflicts"""
    timetable = run_solver()
    validate_no_room_conflicts(timetable)


def test_honours_restriction():
    """Test that honours courses are only in Period 8"""
    timetable = run_solver()
    validate_honours_only_p8(timetable)


def test_mentor_hour_blocked():
    """Test that Tuesday Period 7 is blocked"""
    timetable = run_solver()
    validate_mentor_hour_block(timetable)


def test_open_elective_lock():
    """Test that open electives are in correct slots"""
    timetable = run_solver()
    validate_open_elective_slots(timetable)