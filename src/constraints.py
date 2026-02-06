from collections import defaultdict


def build_conflicts(students, courses):
    student_conflicts = set()

    for course_list in students["courses"]:
        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                a, b = sorted((course_list[i], course_list[j]))
                student_conflicts.add((a, b))

    faculty_conflicts = set()
    faculty_groups = courses.groupby("faculty_id")

    for _, group in faculty_groups:
        ids = list(group["course_id"])
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = sorted((ids[i], ids[j]))
                faculty_conflicts.add((a, b))

    return student_conflicts.union(faculty_conflicts)


def add_conflict_constraints(model, course_slots, conflict_pairs, lab_courses):
    for c1, c2 in conflict_pairs:
        if c1 not in course_slots or c2 not in course_slots:
            continue

        for s1 in course_slots[c1]:
            for s2 in course_slots[c2]:
                model.Add(s1 != s2)

                if c1 in lab_courses:
                    model.Add(s1 + 1 != s2)

                if c2 in lab_courses:
                    model.Add(s2 + 1 != s1)


def add_room_constraints(model, course_slots, room_vars):
    all_slots = defaultdict(list)

    for cid in course_slots:
        for slot in course_slots[cid]:
            all_slots[slot].append(room_vars[cid])

    for room_list in all_slots.values():
        if len(room_list) > 1:
            model.AddAllDifferent(room_list)


def add_fixed_slot_constraints(model, course_slots, courses):
    for cid, slots in course_slots.items():
        course_type = courses.loc[courses["course_id"] == cid, "type"].values[0]

        for slot in slots:

            # Tuesday P7 → Mentor interaction (slot 1*8+6)
            model.Add(slot != 14)

            # P8 → Only honours
            remainder = model.NewIntVar(0, 7, f"{cid}_rem")
            model.AddModuloEquality(remainder, slot, 8)

            if course_type == "honours":
                model.Add(remainder == 7)
            else:
                model.Add(remainder != 7)

            # Open elective fixed slots
            if "Open Elective" in cid:
                model.AddAllowedAssignments(
                    [slot],
                    [[10], [11], [22], [30]]
                )
            else:
                model.Add(slot != 10)
                model.Add(slot != 11)
                model.Add(slot != 22)
                model.Add(slot != 30)
