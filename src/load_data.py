import pandas as pd


def load_data():
    try:
        courses = pd.read_csv("data/courses.csv")
        faculty = pd.read_csv("data/faculty.csv")
        students = pd.read_csv("data/students.csv")
    except Exception as e:
        raise RuntimeError(f"Error loading CSV files: {e}")

    # ---------------------------
    # 1. Column validation
    # ---------------------------
    required_course_cols = {"course_id", "name", "credits", "weekly_hours", "faculty_id"}
    required_faculty_cols = {"faculty_id", "name", "max_hours"}
    required_student_cols = {"student_id", "name", "courses"}

    if not required_course_cols.issubset(courses.columns):
        raise ValueError("courses.csv missing required columns")

    if not required_faculty_cols.issubset(faculty.columns):
        raise ValueError("faculty.csv missing required columns")

    if not required_student_cols.issubset(students.columns):
        raise ValueError("students.csv missing required columns")

    # ---------------------------
    # 2. Uniqueness checks
    # ---------------------------
    if not courses["course_id"].is_unique:
        raise ValueError("Duplicate course_id found in courses.csv")

    if not faculty["faculty_id"].is_unique:
        raise ValueError("Duplicate faculty_id found in faculty.csv")

    if not students["student_id"].is_unique:
        raise ValueError("Duplicate student_id found in students.csv")

    # ---------------------------
    # 3. Type enforcement
    # ---------------------------
    courses["credits"] = pd.to_numeric(courses["credits"], errors="raise")
    courses["weekly_hours"] = pd.to_numeric(courses["weekly_hours"], errors="raise")
    faculty["max_hours"] = pd.to_numeric(faculty["max_hours"], errors="raise")

    # ---------------------------
    # 4. Normalize student course lists
    # ---------------------------
    def parse_courses(course_string):
        if pd.isna(course_string):
            return []

        # Support both "|" and ","
        delimiter = "|" if "|" in course_string else ","
        return [c.strip() for c in course_string.split(delimiter) if c.strip()]

    students["courses"] = students["courses"].apply(parse_courses)

    # ---------------------------
    # 5. Foreign key validation (vectorized & set-based)
    # ---------------------------

    valid_course_ids = set(courses["course_id"])
    valid_faculty_ids = set(faculty["faculty_id"])

    # Validate course → faculty mapping (vectorized)
    if not courses["faculty_id"].isin(valid_faculty_ids).all():
        invalid = courses.loc[
            ~courses["faculty_id"].isin(valid_faculty_ids), "faculty_id"
        ].unique()
        raise ValueError(f"Invalid faculty_id(s) in courses.csv: {invalid}")

    # Validate student course registrations (set difference)
    all_student_courses = set(
        course for sublist in students["courses"] for course in sublist
    )

    invalid_courses = all_student_courses - valid_course_ids
    if invalid_courses:
        raise ValueError(
            f"Invalid course_id(s) referenced in students.csv: {invalid_courses}"
        )

    return courses, faculty, students
