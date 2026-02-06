## AI-Based Timetable Generator (NEP 2020 Compliant)

## Project Overview

This project implements a constraint-based academic timetable generator using Google OR-Tools (CP-SAT solver).

The system generates a feasible timetable from structured input data while enforcing academic and policy constraints aligned with NEP 2020 principles, including credit limits, faculty workload, and conflict prevention.

Input data is provided via CSV files containing:

Course information (credits, weekly hours, faculty)

Faculty details (maximum teaching load)

Student registrations (selected courses)

The output is a conflict-free timetable saved in JSON format.

## Current Implementation

The system currently supports:

CSV-based structured data loading

Constraint modeling using CP-SAT

Student conflict prevention

Faculty scheduling conflict prevention

Faculty workload validation

Semester credit limit validation (NEP-aligned bounds)

JSON timetable export

Basic unit testing for solver execution

The architecture is modular and extensible.

## Project Structure

data/
    courses.csv
    faculty.csv
    students.csv

src/
    load_data.py
    constraints.py
    solver.py
    validate.py
    test_solver.py

output/
    timetable.json

## System Workflow

Data Loading:
Input data is read from CSV files.

Model Construction:
A CP-SAT model is created where each course is assigned a time slot variable.

Constraint Application:
Academic and scheduling constraints are added to the model.

Solving:
The solver searches for a feasible timetable.

Output Generation:
The resulting schedule is exported to output/timetable.json.

## Constraints Implemented

Student Constraints:

No overlapping courses for any student.

Semester credit load must be within defined bounds:

Minimum: 16 credits

Maximum: 24 credits.

Faculty Constraints:

A faculty member cannot teach multiple courses in the same time slot.

Total assigned weekly hours must not exceed the faculty's maximum workload.

Course Constraints:

Each course is assigned exactly one valid time slot.

No two courses share the same slot (global uniqueness).

Time Structure:

5 working days

4 slots per day

Total of 20 scheduling slots

Each slot is mapped to a specific day and time index.

## How to Run

1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Run the solver
python src/solver.py

4. Run tests
python src/test_solver.py

## Output Format

Example:

{
    "C1": {
        "day": "Mon",
        "time": "Slot 1"
    }
}

## Future Work

Planned enhancements include:

Multi-slot allocation for multi-credit courses

Room allocation constraints

Soft constraints (gap minimization, load balancing)

Optimization objectives

Hybrid ML + constraint-based approach

Web interface for visualization