from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from lib.DatabaseManager import DatabaseManager, Faculty, Course, TimeSlot, Schedule, Classroom  # Assuming database_manager.py contains the schema

class CourseScheduler:
    def __init__(self, db_url="sqlite:///test.db"):
        self.db = DatabaseManager(db_url)
        self.db.start_session()
        self.session = self.db.session

    def get_sorted_courses(self, session):
    # Get all courses, sorted:
    #  1. Courses whose associated faculty member has a Preference come first.
    #  2. Within that group, courses with a ReqRoom appear before those without.
        query = session.query(Course).outerjoin(
            Faculty,
            or_(
                Course.CourseID == Faculty.Class1,
                Course.CourseID == Faculty.Class2,
                Course.CourseID == Faculty.Class3
            )
        ).order_by(
            # Within each group, order so that courses with a non-null required room come first
            Course.ReqRoom.isnot(None).desc(),
            # Order so that courses with a non-null faculty Preference come first
            Faculty.Preference.isnot("None").desc()
        )
        return query.all()

    # def assign_time_slot(self, course_id, faculty_id):
    #     """Assign the first available time slot ensuring no professor overlap."""
    #     available_slots = self.session.query(TimeSlot).all()

    #     for slot in available_slots:
    #         if not self.is_professor_occupied(faculty_id, slot.SlotID):
    #             return slot.SlotID

    #     return None  # No available time slot

    # def is_professor_occupied(self, faculty_id, timeslot_id):
    #     """Check if a professor is already scheduled for a given time slot."""
    #     return self.session.query(Schedule).filter(
    #         and_(Schedule.Professor == faculty_id, Schedule.TimeSlot == timeslot_id)
    #     ).count() > 0

    # def assign_room(self, course_id, timeslot_id):
    #     """Assign a room ensuring no conflicts."""
    #     course = self.session.query(Course).filter(Course.CourseID == course_id).first()
    #     required_room = course.ReqRoom

    #     if required_room:
    #         if not self.is_room_occupied(required_room, timeslot_id):
    #             return required_room  # Assign the required room if it's available

    #     # Otherwise, pick the first available room
    #     available_rooms = self.session.query(Classroom).all()
    #     for room in available_rooms:
    #         if not self.is_room_occupied(room.RoomID, timeslot_id):
    #             return room.RoomID

    #     return None  # No available room found

    # def is_room_occupied(self, room_id, timeslot_id):
    #     """Check if a room is already in use for a specific time slot."""
    #     return self.session.query(Schedule).filter(
    #         and_(Schedule.Classroom == room_id, Schedule.TimeSlot == timeslot_id)
    #     ).count() > 0

    # def commit_schedule(self, course_id, faculty_id, timeslot_id, room_id):
    #     """Insert a finalized schedule entry into the database."""
    #     schedule_entry = Schedule(TimeSlot=timeslot_id, Professor=faculty_id, Course=course_id, Classroom=room_id)
    #     self.session.add(schedule_entry)
    #     self.db.safe_commit()

    # def generate_schedule(self):
    #     """Main scheduling algorithm ensuring no professor or room overlaps."""
    #     sorted_courses = self.sort_courses_by_preference()

    #     for course_id in sorted_courses:
    #         faculty_id = self.get_faculty_for_course(course_id)
    #         if not faculty_id:
    #             continue  # Skip if no faculty assigned

    #         timeslot_id = self.assign_time_slot(course_id, faculty_id)
    #         if timeslot_id is None:
    #             continue  # No available time slot

    #         room_id = self.assign_room(course_id, timeslot_id)
    #         if room_id is None:
    #             continue  # No available room

    #         self.commit_schedule(course_id, faculty_id, timeslot_id, room_id)

    # def get_faculty_for_course(self, course_id):
    #     """Retrieve the assigned faculty member for a given course."""
    #     faculty = self.session.query(Faculty).filter(
    #         (Faculty.Class1 == course_id) | (Faculty.Class2 == course_id) | (Faculty.Class3 == course_id)
    #     ).first()
    #     return faculty.FacultyID if faculty else None


if __name__ == "__main__":
    scheduler = CourseScheduler()
    #scheduler.generate_schedule()

    
    sorted_courses = scheduler.get_sorted_courses(scheduler.session)
    for course in sorted_courses:
        print(f"CourseID: {course.CourseID}, Required Room: {course.ReqRoom}")  