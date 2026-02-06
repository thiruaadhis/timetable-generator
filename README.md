## AI-Based Timetable Generator (NEP 2020 Aligned)
## Project Overview

This project implements a constraint-based university timetable generator using Google OR-Tools (CP-SAT solver).

The system generates a feasible weekly timetable from structured institutional data while enforcing academic and operational constraints such as:

Student conflict prevention

Faculty conflict prevention

Faculty workload validation

Semester credit limits

Lab scheduling rules

The generated timetable represents a single week, which repeats throughout the academic month.

Input data is provided through CSV files containing:

Course metadata (credits, weekly hours, faculty mapping)

Faculty workload limits

Student course registrations

The output is exported as a structured JSON timetable.

## Current Implementation

The system currently supports:

Robust CSV data validation and ingestion

6 working days (Monday–Saturday)

4 periods per day

Total 24 scheduling slots per week

Student conflict graph construction (optimized)

Faculty conflict graph construction (optimized)

Lab course handling (2 consecutive periods)

Faculty workload validation

Semester credit validation

JSON timetable export

Parallel CP-SAT solving with performance tuning

The architecture is modular and scalable.

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

1. Data Loading

CSV files are validated for schema correctness.

Foreign key relationships are verified.

Student course lists are normalized.

2. Model Construction

Each course is assigned a time slot variable (0–23).

Lab courses are identified automatically based on weekly hours.

3. Conflict Graph Construction

Student conflicts are precomputed.

Faculty conflicts are precomputed.

Duplicate constraint creation is avoided for efficiency.

4. Constraint Application

The solver enforces:

Student time conflicts

Faculty time conflicts

Lab structural constraints (2 consecutive periods)

Lab cannot start in last period of day

Faculty workload validation

Credit bounds validation

5. Solving

CP-SAT solver runs with parallel workers.

Time limit applied for controlled solving.

6. Output Generation

Weekly timetable is generated.

Saved to output/timetable.json.

## Constraints Implemented
Student Constraints

A student cannot attend overlapping courses.

Lab courses block two consecutive periods.

Semester credit load must lie within:

Minimum: 16 credits

Maximum: 24 credits

Faculty Constraints

Faculty cannot teach overlapping courses.

Lab courses block two consecutive periods.

Total assigned teaching load must not exceed defined maximum hours.

Lab Constraints

Lab courses occupy two consecutive periods.

Labs cannot start in the last period of a day.

Lab conflicts are checked against both occupied periods.

## Time Structure

6 working days (Mon–Sat)

4 periods per day

24 total weekly slots

Improvements Over Initial Version

Removed unrealistic global “one course per slot” constraint.

Optimized conflict modeling using precomputed conflict graphs.

Eliminated redundant constraint generation.

Added lab structure enforcement.

Improved solver performance with multi-threading.

Added robust input validation layer.

Ensured consistent weekly timetable logic.

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
    "CSE201": {
        "day": "Mon",
        "period": "Period 1"
    },
    "ECE202": {
        "day": "Wed",
        "periods": ["Period 2", "Period 3"]
    }
}


Theory courses contain a single period.
Lab courses contain two consecutive periods.

## What Is Not Yet Implemented

The system currently focuses on hard feasibility constraints. The following enhancements are planned:

Multi-slot modeling for theory courses based on full weekly hours

Room allocation constraints

Department/semester-level scheduling partitions

Soft constraints (minimize gaps, balance daily load)

Optimization objective functions

Section-wise timetable generation

Instructor preference modeling

Graphical visualization interface

## Long-Term Vision

This system aims to evolve into a scalable institutional scheduling engine capable of:

Supporting multi-department universities

Handling realistic weekly hour allocations

Incorporating room and infrastructure constraints

Optimizing timetable quality

Integrating hybrid ML + constraint-based optimization