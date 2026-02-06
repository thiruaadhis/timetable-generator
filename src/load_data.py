import pandas as pd

def load_data():
    courses = pd.read_csv("data/courses.csv")
    faculty = pd.read_csv("data/faculty.csv")
    students = pd.read_csv("data/students.csv")

    # Convert student course string to list
    students["courses"] = students["courses"].apply(lambda x: x.split("|"))

    return courses, faculty, students
