def validate_no_conflicts(timetable):
    seen = {}

    for course, info in timetable.items():
        key = (info["day"], info["time"])

        if key in seen:
            raise ValueError("Conflict detected!")
        seen[key] = course

    return True
