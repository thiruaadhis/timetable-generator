from collections import defaultdict

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS = [f"Period {i}" for i in range(1, 9)]


# -------------------------------------------------
# 1️⃣ Slot range validation
# -------------------------------------------------
def validate_slot_range(timetable):
    for dept in timetable:
        for day in timetable[dept]:
            assert day in DAYS, f"Invalid day {day}"

            for period in timetable[dept][day]:
                assert period in PERIODS, f"Invalid period {period}"


# -------------------------------------------------
# 2️⃣ Lab must occupy two consecutive periods
# -------------------------------------------------
def validate_lab_consecutive(timetable):
    for dept in timetable:
        for day in timetable[dept]:
            periods = sorted(
                timetable[dept][day].keys(),
                key=lambda x: int(x.split()[1])
            )

            for i, period in enumerate(periods):
                entry = timetable[dept][day][period]
                course = entry["course"]

                if "Laboratory" in course or "Lab" in course:
                    period_number = int(period.split()[1])

                    # Must have next consecutive period
                    next_period = f"Period {period_number + 1}"
                    assert next_period in timetable[dept][day], \
                        f"{course} not consecutive in {dept} on {day}"

                    # Must be same course in next period
                    next_course = timetable[dept][day][next_period]["course"]
                    assert next_course == course, \
                        f"{course} split incorrectly in {dept} on {day}"


# -------------------------------------------------
# 3️⃣ No room conflicts across departments
# -------------------------------------------------
def validate_no_room_conflicts(timetable):
    room_usage = defaultdict(list)

    for dept in timetable:
        for day in timetable[dept]:
            for period in timetable[dept][day]:
                room = timetable[dept][day][period]["room"]

                key = (day, period, room)
                room_usage[key].append(dept)

    for key, depts in room_usage.items():
        assert len(depts) == 1, \
            f"Room conflict in {key} between {depts}"


# -------------------------------------------------
# 4️⃣ Honours only in Period 8
# -------------------------------------------------
def validate_honours_only_p8(timetable):
    for dept in timetable:
        for day in timetable[dept]:
            for period in timetable[dept][day]:
                course = timetable[dept][day][period]["course"]

                if "Honours" in course:
                    assert period == "Period 8", \
                        f"Honours scheduled outside P8 in {dept} {day}"


# -------------------------------------------------
# 5️⃣ Tuesday Period 7 must be Mentor Interaction
# -------------------------------------------------
def validate_mentor_hour_block(timetable):
    for dept in timetable:
        if "Tue" in timetable[dept]:
            if "Period 7" in timetable[dept]["Tue"]:
                course = timetable[dept]["Tue"]["Period 7"]["course"]
                assert course == "Mentor Interaction", \
                    f"Tuesday P7 not Mentor Interaction in {dept}"


# -------------------------------------------------
# 6️⃣ Open Elective lock
# -------------------------------------------------
def validate_open_elective_slots(timetable):
    allowed = {
        ("Tue", "Period 3"),
        ("Tue", "Period 4"),
        ("Wed", "Period 7"),
        ("Thu", "Period 7"),
    }

    for dept in timetable:
        for day in timetable[dept]:
            for period in timetable[dept][day]:
                course = timetable[dept][day][period]["course"]

                if "Open Elective" in course:
                    assert (day, period) in allowed, \
                        f"Open Elective wrongly scheduled in {dept} {day} {period}"
