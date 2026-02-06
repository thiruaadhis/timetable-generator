import json
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS = [f"Period {i}" for i in range(1, 9)]

OUTPUT_PATH = Path("output/timetable.json")
console = Console()


def load_timetable():
    return json.loads(OUTPUT_PATH.read_text())


def build_grid(dept_data):
    grid = defaultdict(lambda: defaultdict(str))

    for day, periods in dept_data.items():
        for period, details in periods.items():
            display = (
                f"[cyan]{details['course']}[/cyan]\n"
                f"[yellow]{details['faculty']}[/yellow]\n"
                f"[green]{details['room']}[/green]"
            )
            grid[day][period] = display

    return grid


def print_table(dept, grid):
    console.rule(f"[bold magenta]{dept} WEEKLY TIMETABLE")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Day", style="bold white", width=10)

    for i in range(1, 9):
        table.add_column(f"P{i}", justify="center", width=28)

    for day in DAYS:
        row = [day]
        for period in PERIODS:
            row.append(grid[day][period] if grid[day][period] else "[dim]---[/dim]")
        table.add_row(*row)

    console.print(table)


def render():
    timetable = load_timetable()

    for dept, dept_data in timetable.items():
        grid = build_grid(dept_data)
        print_table(dept, grid)


def main():
    render()


if __name__ == "__main__":
    main()
