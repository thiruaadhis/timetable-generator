import pandas as pd
import os


def load_data():
    """Load all CSV data files from the data directory"""
    # Get absolute path to the project root (parent of src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    
    # Load all CSV files
    courses = pd.read_csv(os.path.join(data_dir, "courses.csv"))
    faculty = pd.read_csv(os.path.join(data_dir, "faculty.csv"))
    students = pd.read_csv(os.path.join(data_dir, "students.csv"))
    rooms = pd.read_csv(os.path.join(data_dir, "rooms.csv"))

    # Parse pipe-separated course lists for students
    def parse_courses(course_string):
        return [x.strip() for x in course_string.split("|")]

    students["courses"] = students["courses"].apply(parse_courses)

    return courses, faculty, students, rooms