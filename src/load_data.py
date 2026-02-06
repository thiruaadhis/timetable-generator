import pandas as pd


def load_data():
    courses = pd.read_csv("data/courses.csv")
    faculty = pd.read_csv("data/faculty.csv")
    students = pd.read_csv("data/students.csv")
    rooms = pd.read_csv("data/rooms.csv")

    def parse_courses(c):
        return [x.strip() for x in c.split("|")]

    students["courses"] = students["courses"].apply(parse_courses)

    return courses, faculty, students, rooms
