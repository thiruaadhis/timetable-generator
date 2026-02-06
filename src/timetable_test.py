import json
from pathlib import Path
from collections import defaultdict

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS = ["Period 1", "Period 2", "Period 3", "Period 4"]

OUTPUT_PATH = Path("output/timetable.json")


def load_timetable():
    if not OUTPUT_PATH.exists():
        raise FileNotFoundError("Run solver first.")
    return json.loads(OUTPUT_PATH.read_text())


def build_grid(dept_data):
    grid = defaultdict(lambda: defaultdict(list))

    for course_id, entry in dept_data.items():
        day = entry["day"]

        if "period" in entry:
            grid[day][entry["period"]].append(course_id)
        else:
            for period in entry["periods"]:
                grid[day][period].append(f"{course_id} (Lab)")

    return grid


def print_table(dept, grid):
    print(f"\n========== {dept} TIMETABLE ==========\n")

    header = ["Day"] + PERIODS
    print("{:<8} {:<20} {:<20} {:<20} {:<20}".format(*header))
    print("-" * 100)

    for day in DAYS:
        row = [day]
        for period in PERIODS:
            courses = ", ".join(grid[day][period])
            row.append(courses)

        print("{:<8} {:<20} {:<20} {:<20} {:<20}".format(*row))


def main():
    timetable = load_timetable()

    for dept, dept_data in timetable.items():
        grid = build_grid(dept_data)
        print_table(dept, grid)


if __name__ == "__main__":
    main()
