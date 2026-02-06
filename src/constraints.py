from ortools.sat.python import cp_model


TOTAL_SLOTS = 20  # 5 days × 4 slots


def add_basic_constraints(model, course_slots):
    # No two courses in same slot
    model.AddAllDifferent(course_slots.values())


def add_student_constraints(model, course_slots, students):
    for _, row in students.iterrows():
        courses = row["courses"]

        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                c1 = courses[i]
                c2 = courses[j]

                if c1 in course_slots and c2 in course_slots:
                    model.Add(course_slots[c1] != course_slots[c2])


def add_faculty_constraints(model, course_slots, courses, faculty):
    for _, f in faculty.iterrows():
        faculty_courses = courses[courses["faculty_id"] == f["faculty_id"]]

        assigned = []

        for _, c in faculty_courses.iterrows():
            course_id = c["course_id"]
            if course_id in course_slots:
                assigned.append(course_slots[course_id])

        if len(assigned) > 1:
            model.AddAllDifferent(assigned)


def add_faculty_workload_constraint(model, courses, faculty):
    # NEP-style reasonable workload constraint
    for _, f in faculty.iterrows():
        faculty_courses = courses[courses["faculty_id"] == f["faculty_id"]]

        total_hours = faculty_courses["weekly_hours"].sum()

        if total_hours > f["max_hours"]:
            raise ValueError(
                f"Faculty {f['faculty_id']} exceeds max workload!"
            )


def add_credit_constraints(students, courses):
    # NEP 2020 typical semester credit bounds
    MIN_CREDITS = 16
    MAX_CREDITS = 24

    course_credit_map = dict(zip(courses["course_id"], courses["credits"]))

    for _, s in students.iterrows():
        total = sum(course_credit_map[c] for c in s["courses"] if c in course_credit_map)

        if total < MIN_CREDITS or total > MAX_CREDITS:
            raise ValueError(
                f"Student {s['student_id']} violates NEP credit limits!"
            )


def add_faculty_daily_load_constraint(
        # enforces that no faculty teaches more than their max hours in a single day
    model, course_slots, courses, faculty, days, slots_per_day
):
    for _, f in faculty.iterrows():
        faculty_id = f["faculty_id"]
        max_per_day = f["max_hours"]  # treat as per-day limit

        faculty_courses = courses[courses["faculty_id"] == faculty_id]

        for d in range(len(days)):
            daily_classes = []

            for _, c in faculty_courses.iterrows():
                cid = c["course_id"]
                if cid not in course_slots:
                    continue

                # Boolean: is this course on day d?
                on_day = model.NewBoolVar(f"{cid}_day_{d}")

                slot = course_slots[cid]

                model.Add(slot // slots_per_day == d).OnlyEnforceIf(on_day)
                model.Add(slot // slots_per_day != d).OnlyEnforceIf(on_day.Not())

                daily_classes.append(on_day)

            if daily_classes:
                model.Add(sum(daily_classes) <= max_per_day)
