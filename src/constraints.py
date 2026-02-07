from collections import defaultdict

# Constants for fixed time slots
MENTOR_HOUR_SLOT = 14  # Tuesday Period 7 (1*8 + 6)
OPEN_ELECTIVE_SLOTS = [10, 11, 22, 30]  # Tue P3, Tue P4, Wed P7, Thu P7
PERIOD_8_OFFSET = 7  # Remainder when slot % 8 == 7


def build_conflicts(students, courses):
    """
    Build conflict pairs from student enrollments and faculty assignments.
    Two courses conflict if:
    - Same student is enrolled in both
    - Same faculty teaches both
    """
    student_conflicts = set()

    # Student conflicts: courses taken by same student can't overlap
    for course_list in students["courses"]:
        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                a, b = sorted((course_list[i], course_list[j]))
                student_conflicts.add((a, b))

    # Faculty conflicts: courses taught by same professor can't overlap
    faculty_conflicts = set()
    faculty_groups = courses.groupby("faculty_id")

    for _, group in faculty_groups:
        course_ids = list(group["course_id"])
        for i in range(len(course_ids)):
            for j in range(i + 1, len(course_ids)):
                a, b = sorted((course_ids[i], course_ids[j]))
                faculty_conflicts.add((a, b))

    return student_conflicts.union(faculty_conflicts)


def add_conflict_constraints(model, course_slots, conflict_pairs, lab_courses):
    """
    Ensure conflicting courses are not scheduled at the same time.
    For labs, also ensure they don't conflict with the consecutive period.
    """
    for c1, c2 in conflict_pairs:
        if c1 not in course_slots or c2 not in course_slots:
            continue

        for s1 in course_slots[c1]:
            for s2 in course_slots[c2]:
                # Basic conflict: different slots
                model.Add(s1 != s2)

                # If c1 is a lab, its second period can't conflict with c2
                if c1 in lab_courses:
                    model.Add(s1 + 1 != s2)

                # If c2 is a lab, its second period can't conflict with c1
                if c2 in lab_courses:
                    model.Add(s2 + 1 != s1)


def add_room_constraints(model, course_slots, room_vars, total_slots, num_rooms):
    """
    Prevent room conflicts: no two courses can use the same room at the same time.
    
    Uses conditional constraints:
    - If course1 and course2 are in the same slot, they must use different rooms
    """
    all_courses = list(course_slots.keys())
    
    # Check every pair of courses
    for i, c1 in enumerate(all_courses):
        for c2 in all_courses[i+1:]:
            # For each time slot of c1 and each time slot of c2
            for slot1 in course_slots[c1]:
                for slot2 in course_slots[c2]:
                    # Create boolean: are they in the same slot?
                    same_slot = model.NewBoolVar(f'{c1}_{c2}_same_{id(slot1)}_{id(slot2)}')
                    
                    # If same slot, enforce different rooms
                    model.Add(slot1 == slot2).OnlyEnforceIf(same_slot)
                    model.Add(slot1 != slot2).OnlyEnforceIf(same_slot.Not())
                    model.Add(room_vars[c1] != room_vars[c2]).OnlyEnforceIf(same_slot)


def add_fixed_slot_constraints(model, course_slots, courses):
    """
    Add constraints for fixed time slots:
    - Tuesday P7 (slot 14) is blocked for Mentor Interaction
    - Period 8 (slots 7, 15, 23, 31, 39, 47) is reserved for Honours courses only
    - Open Electives must be in specific slots: Tue P3, Tue P4, Wed P7, Thu P7
    """
    for cid, slots in course_slots.items():
        # Get course information
        course_row = courses.loc[courses["course_id"] == cid]
        course_type = course_row["type"].values[0]
        course_name = course_row["name"].values[0]

        for slot in slots:
            # Block Tuesday P7 for everyone (Mentor Hour)
            model.Add(slot != MENTOR_HOUR_SLOT)

            # Period 8 constraint
            remainder = model.NewIntVar(0, 7, f"{cid}_slot{id(slot)}_rem")
            model.AddModuloEquality(remainder, slot, 8)

            if course_type == "honours":
                # Honours courses MUST be in Period 8
                model.Add(remainder == PERIOD_8_OFFSET)
            else:
                # Non-honours courses CANNOT be in Period 8
                model.Add(remainder != PERIOD_8_OFFSET)

            # Open Elective constraint - check by course name
            if "Open Elective" in course_name:
                # Must be in one of the allowed slots
                model.AddAllowedAssignments(
                    [slot],
                    [[s] for s in OPEN_ELECTIVE_SLOTS]
                )
            else:
                # Non-open-elective courses cannot use these slots
                for oe_slot in OPEN_ELECTIVE_SLOTS:
                    model.Add(slot != oe_slot)


def add_room_type_constraints(model, room_vars, courses, rooms):
    """
    Ensure room types match course types:
    - Lab courses must use lab rooms
    - Theory/Honours courses must use lecture rooms
    """
    # Get indices of each room type
    lecture_room_indices = [i for i, row in rooms.iterrows() if row["type"] == "lecture"]
    lab_room_indices = [i for i, row in rooms.iterrows() if row["type"] == "lab"]
    
    for _, course in courses.iterrows():
        cid = course["course_id"]
        course_type = course["type"]
        
        if cid not in room_vars:
            continue
        
        if course_type == "lab":
            # Labs can only use lab rooms
            model.AddAllowedAssignments(
                [room_vars[cid]], 
                [[i] for i in lab_room_indices]
            )
        else:
            # Theory and Honours courses use lecture rooms
            model.AddAllowedAssignments(
                [room_vars[cid]], 
                [[i] for i in lecture_room_indices]
            )