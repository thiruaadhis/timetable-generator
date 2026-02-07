from collections import defaultdict

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS = [f"Period {i}" for i in range(1, 9)]


def validate_slot_range(timetable):
    """Ensure all days and periods are valid"""
    for dept in timetable:
        for day in timetable[dept]:
            assert day in DAYS, f"Invalid day {day}"
            
            for period in timetable[dept][day]:
                assert period in PERIODS, f"Invalid period {period}"


def validate_lab_consecutive(timetable):
    """Ensure lab courses occupy two consecutive periods"""
    for dept in timetable:
        for day in timetable[dept]:
            periods = sorted(
                timetable[dept][day].keys(),
                key=lambda x: int(x.split()[1])
            )
            
            for period in periods:
                entry = timetable[dept][day][period]
                course = entry["course"]
                
                if "Laboratory" in course or "Lab" in course:
                    period_number = int(period.split()[1])
                    next_period = f"Period {period_number + 1}"
                    
                    # Must have next consecutive period
                    assert next_period in timetable[dept][day], \
                        f"{course} not consecutive in {dept} on {day}"
                    
                    # Must be same course in next period
                    next_course = timetable[dept][day][next_period]["course"]
                    assert next_course == course, \
                        f"{course} split incorrectly in {dept} on {day}"


def validate_no_room_conflicts(timetable):
    """Ensure no room is used by multiple departments at the same time"""
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


def validate_honours_only_p8(timetable):
    """Ensure honours courses are only in Period 8"""
    for dept in timetable:
        for day in timetable[dept]:
            for period in timetable[dept][day]:
                course = timetable[dept][day][period]["course"]
                
                if "Honours" in course:
                    assert period == "Period 8", \
                        f"Honours scheduled outside P8 in {dept} {day}"


def validate_mentor_hour_block(timetable):
    """Ensure Tuesday Period 7 is empty (Mentor Interaction)"""
    for dept in timetable:
        if "Tue" in timetable[dept]:
            assert "Period 7" not in timetable[dept]["Tue"], \
                f"Tuesday P7 should be blocked in {dept}"


def validate_open_elective_slots(timetable):
    """Ensure open electives are only in allowed slots"""
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