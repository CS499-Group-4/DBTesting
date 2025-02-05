from lib.DatabaseManager import DatabaseManager

dbm = DatabaseManager()

dbm.start_session()

dbm.add_faculty("Dr. Smith", "CSC 101", "CSC 102", "CSC 103", "MWF")
dbm.add_classroom("SH101", "Science Hall", "101")
dbm.add_course("CSC 101", "Intro to Computer Science", 1)
dbm.add_timeslot("MWF", "10:00 AM")
dbm.add_conflict("H", "Room")
dbm.add_schedule(1, 1, 1, 1, 1)


print("Faculty Table")
for faculty in dbm.get_faculty():
    print(f"- {faculty.Name}")

print("\nClassroom Table")
for classroom in dbm.get_classroom():
    print(f"- {classroom.Building}, Room {classroom.Room}")

print("\nCourse Table")
for course in dbm.get_course():
    print(f"- {course.Name}")


dbm.end_session()