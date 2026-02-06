from ortools.sat.python import cp_model


def build_student_conflict_graph(students):
    conflict_pairs = set()

    for courses in students["courses"]:
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                c1, c2 = sorted((courses[i], courses[j]))
                conflict_pairs.add((c1, c2))

    return conflict_pairs


def build_faculty_conflict_graph(courses):
    conflict_pairs = set()

    faculty_groups = courses.groupby("faculty_id")

    for _, group in faculty_groups:
        course_ids = list(group["course_id"])
        for i in range(len(course_ids)):
            for j in range(i + 1, len(course_ids)):
                c1, c2 = sorted((course_ids[i], course_ids[j]))
                conflict_pairs.add((c1, c2))

    return conflict_pairs


def add_conflict_constraints(model, course_slots, conflict_pairs, lab_courses):
    for c1, c2 in conflict_pairs:
        if c1 not in course_slots or c2 not in course_slots:
            continue

        v1 = course_slots[c1]
        v2 = course_slots[c2]

        # theory-theory
        if c1 not in lab_courses and c2 not in lab_courses:
            model.Add(v1 != v2)

        # lab-theory
        elif c1 in lab_courses and c2 not in lab_courses:
            model.Add(v2 != v1)
            model.Add(v2 != v1 + 1)

        elif c2 in lab_courses and c1 not in lab_courses:
            model.Add(v1 != v2)
            model.Add(v1 != v2 + 1)

        # lab-lab
        else:
            model.Add(v1 != v2)
            model.Add(v1 != v2 + 1)
            model.Add(v1 + 1 != v2)
            model.Add(v1 + 1 != v2 + 1)


def add_lab_structure_constraints(model, course_slots, lab_courses, slots_per_day):
    for lab in lab_courses:
        if lab in course_slots:
            slot = course_slots[lab]

            # Create remainder variable
            remainder = model.NewIntVar(0, slots_per_day - 1, f"{lab}_rem")

            # remainder = slot % slots_per_day
            model.AddModuloEquality(remainder, slot, slots_per_day)

            # Prevent lab from starting at last period
            model.Add(remainder != slots_per_day - 1)
