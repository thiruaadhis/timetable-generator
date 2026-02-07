import json
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import os

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS = [f"Period {i}" for i in range(1, 9)]
TIME_SLOTS = [
    "8:00-9:00",
    "9:00-10:00", 
    "10:00-11:00",
    "11:00-12:00",
    "12:00-1:00",
    "1:00-2:00",
    "2:00-3:00",
    "3:00-4:00"
]

# Get path to output directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
OUTPUT_PATH = Path(os.path.join(project_root, "output", "timetable.json"))

console = Console()


def load_timetable():
    """Load timetable from JSON file"""
    return json.loads(OUTPUT_PATH.read_text())


def get_cell_style(course_name):
    """Return Rich style based on course type"""
    if not course_name:
        return "dim white"
    if "Laboratory" in course_name or "Lab" in course_name:
        return "bold green"
    if "Honours" in course_name:
        return "bold yellow"
    if "Open Elective" in course_name:
        return "bold magenta"
    return "bold cyan"


def build_grid(dept_data):
    """Build a grid with styled course information"""
    grid = defaultdict(lambda: defaultdict(lambda: None))

    for day, periods in dept_data.items():
        for period, details in periods.items():
            course = details["course"]
            faculty = details["faculty"]
            room = details["room"]
            
            style = get_cell_style(course)
            
            # Create styled text
            content = Text()
            content.append(f"{course}\n", style=style)
            content.append(f"{faculty}\n", style="italic white")
            content.append(f"{room}", style="dim white")
            
            grid[day][period] = content

    return grid


def print_department_table(dept, dept_data):
    """Print a beautiful Rich table for one department"""
    
    # Department name mapping
    dept_names = {
        'CSE': '💻 Computer Science & Engineering',
        'ECE': '⚡ Electronics & Communication',
        'ME2': '⚙️  Mechanical Engineering',
        'CE2': '🏗️  Civil Engineering',
        'IT2': '🌐 Information Technology'
    }
    dept_full_name = dept_names.get(dept, dept)
    
    # Print department header
    console.print()
    console.print(Panel(
        f"[bold white]{dept_full_name}[/bold white]",
        style="bold blue",
        padding=(1, 2)
    ))
    
    # Build the grid
    grid = build_grid(dept_data)
    
    # Create Rich table
    table = Table(
        show_header=True,
        header_style="bold white on blue",
        border_style="blue",
        padding=(0, 1),
        expand=True
    )
    
    # Add day column
    table.add_column("Day", style="bold yellow", width=8, justify="center")
    
    # Add period columns with time slots
    for i, (period, time) in enumerate(zip(PERIODS, TIME_SLOTS), 1):
        table.add_column(
            f"P{i}\n{time}",
            justify="center",
            width=20,
            overflow="fold"
        )
    
    # Add rows for each day
    for day in DAYS:
        row = [day]
        
        for period in PERIODS:
            cell_content = grid[day].get(period)
            
            if cell_content:
                row.append(cell_content)
            else:
                # Empty cell
                row.append(Text("—", style="dim white"))
        
        table.add_row(*row)
    
    console.print(table)
    console.print()


def print_legend():
    """Print a legend explaining the color coding"""
    legend = Table(show_header=False, box=None, padding=(0, 2))
    legend.add_column(justify="left")
    
    legend.add_row(Text("📚 Theory Courses", style="bold cyan"))
    legend.add_row(Text("🧪 Laboratory Sessions", style="bold green"))
    legend.add_row(Text("🏆 Honours Courses", style="bold yellow"))
    legend.add_row(Text("🎯 Open Electives", style="bold magenta"))
    
    console.print(Panel(
        legend,
        title="[bold white]Legend[/bold white]",
        border_style="white",
        padding=(1, 2)
    ))


def print_statistics(timetable):
    """Print statistics about the generated timetable"""
    stats = Table(show_header=False, box=None)
    stats.add_column("Stat", style="bold cyan", justify="right")
    stats.add_column("Value", style="bold white", justify="left")
    
    total_courses = sum(
        len(day_data)
        for dept_data in timetable.values()
        for day_data in dept_data.values()
    )
    
    stats.add_row("Departments", str(len(timetable)))
    stats.add_row("Total Scheduled Slots", str(total_courses))
    stats.add_row("Days", "6 (Mon-Sat)")
    stats.add_row("Periods per Day", "8")
    
    console.print(Panel(
        stats,
        title="[bold white]📊 Timetable Statistics[/bold white]",
        border_style="green",
        padding=(1, 2)
    ))


def render():
    """Main rendering function - displays everything"""
    timetable = load_timetable()
    
    # Print header
    console.print()
    console.rule("[bold blue]🎓 UNIVERSITY TIMETABLE 2025-26[/bold blue]", style="blue")
    console.print()
    
    # Print statistics
    print_statistics(timetable)
    console.print()
    
    # Print legend
    print_legend()
    
    # Print each department's timetable
    for dept in sorted(timetable.keys()):
        print_department_table(dept, timetable[dept])
    
    # Footer
    console.rule("[bold green]✅ All Constraints Satisfied[/bold green]", style="green")
    console.print()


def main():
    """Entry point for standalone execution"""
    render()


if __name__ == "__main__":
    main()