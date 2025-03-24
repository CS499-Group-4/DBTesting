from sqlalchemy import Column, Integer, String, Enum, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError


#from colorama import Fore, Style, init

Base = declarative_base()

# Faculty table
class Faculty(Base):
    __tablename__ = 'faculty'
    FacultyID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    Name = Column(String, nullable=False, unique=True)
    Class1 = Column(String, ForeignKey('course.CourseID'),nullable=True)
    Class2 = Column(String, ForeignKey('course.CourseID'), nullable=True)
    Class3 = Column(String, ForeignKey('course.CourseID'), nullable=True)
    Preference = Column(String, nullable=True)

# Classroom table
class Classroom(Base):
    __tablename__ = 'classroom'
    RoomID = Column(String, primary_key=True, unique=True)
    Building = Column(String, nullable=False)
    Room = Column(String, nullable=False)

# Course table
class Course(Base):
    __tablename__ = 'course'
    CourseID = Column(String, primary_key=True, unique=True)
    ReqRoom = Column(Integer, nullable=True)
    # ReqRoom = Column(Integer, ForeignKey('classroom.RoomID'), nullable=True)  # Uncomment for foreign key

# TimeSlot table
class TimeSlot(Base):
    __tablename__ = 'timeslot'
    SlotID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    Days = Column(String, nullable=False)  # MW/TR
    StartTime = Column(String, nullable=False)

# Conflict table
class ScheduleConflict(Base):
    __tablename__ = 'schedule_conflict'
    ConflictID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    SchedID = Column(Integer, ForeignKey('schedule.SchedID'), nullable=False)
    GroupID = Column(Integer, ForeignKey('conflict_group.GroupID'), nullable=False)

# Conflict Group table
class ConflictGroup(Base):
    __tablename__ = 'conflict_group'
    GroupID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    Type = Column(String, nullable=False)  # Room, Professor, Preference (probably will be enum later)


# Schedule table
class Schedule(Base):
    __tablename__ = 'schedule'
    SchedID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    TimeSlot = Column(Integer, ForeignKey('timeslot.SlotID'), nullable=True)
    Professor = Column(Integer, ForeignKey('faculty.FacultyID'), nullable=False)
    Course = Column(Integer, ForeignKey('course.CourseID'), nullable=False)
    Classroom = Column(Integer, ForeignKey('classroom.RoomID'),nullable=True)

class DatabaseManager:
    def __init__(self, database_url="sqlite:///test.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        # self.session = sessionmaker(bind=self.engine) #create session
        # self.session = self.session() #start session

    # Ends the session
    def end_session(self):
        self.session.close()

    # Starts the session
    def start_session(self):
        self.session = sessionmaker(bind=self.engine)
        self.session = self.session()

    # Commits transactions for the DB, while catching/handling errors
    def safe_commit(self):
        try:
            self.session.commit()
        except IntegrityError as e:
            print("\n[WARN] IntegrityError occurred:")
            print(f"    {e.orig.args[0]}")
            print("    Please check constraints like unique or foreign key violations.\n")
            self.session.rollback()
        except Exception as e:
            print("\n[ERROR] An unexpected error occurred:")
            print(f"    {str(e)}\n")
            self.session.rollback()


    # Functions for adding entries to the database
    def add_faculty(self, name, class1, class2, class3, preference=None):
        faculty = Faculty(Name=name, Class1=class1, Class2=class2, Class3=class3, Preference=preference)
        self.session.add(faculty)
        self.safe_commit()

    def add_classroom(self, room_id, building, room):
        classroom = Classroom(RoomID=room_id, Building=building, Room=room)
        self.session.add(classroom)
        self.safe_commit()

    def add_course(self, course_id, req_room=None):
        course = Course(CourseID=course_id, ReqRoom=req_room)
        self.session.add(course)
        self.safe_commit()

    def add_timeslot(self, days, start_time):
        timeslot = TimeSlot(Days=days, StartTime=start_time)
        self.session.add(timeslot)
        self.safe_commit()

    def add_conflict_group(self, conflict_type):
        conflict_group = ConflictGroup(Type=conflict_type)
        self.session.add(conflict_group)
        self.safe_commit()

    def add_schedule_conflict(self, sched_id, group_id):
        conflict = ScheduleConflict(SchedID=sched_id, GroupID=group_id)
        self.session.add(conflict)
        self.safe_commit()

    def add_schedule(self, timeslot, faculty, course, classroom):
        schedule = Schedule(TimeSlot=timeslot.SlotID, Professor=faculty.FacultyID, Course=course.CourseID, Classroom=classroom.RoomID)
        self.session.add(schedule)
        self.safe_commit()

    def DEBUG_add_schedule_manual(self, timeslot, faculty, course, classroom):
        schedule = Schedule(TimeSlot=timeslot, Professor=faculty, Course=course, Classroom=classroom)
        self.session.add(schedule)
        self.safe_commit()

    # Simple query functions
    def get_faculty(self):
        return self.session.query(Faculty).all()

    def get_classrooms(self):
        return self.session.query(Classroom).all()
    
    def get_course(self):
        return self.session.query(Course).all()
    
    def get_timeslot(self):
        return self.session.query(TimeSlot).all()
    
    def get_conflict(self):
        return self.session.query(ScheduleConflict).all()

    def get_conflictGroup(self):
        return self.session.query(ConflictGroup).all()
    

# # Example usage
# if __name__ == "__main__":
#     # Replace 'sqlite:///test.db' with your actual database URL
#     session = setup_database('sqlite:///test.db')
#     add_faculty(session, name="Dr. Smith", class1="Math 101", preference="Morning")
#     add_classroom(session, room_id="SH101", building="Science Hall", room="101")
#     add_course(session, course_id= "Bio 101", name="Biology 101", req_room=1)
#     add_timeslot(session, days="MW", start_time="10:00 AM")
#     add_conflict(session, severity="H", conflict_type="Room")
#     add_schedule(session, timeslot=1, faculty=1, course=1, classroom=1, conflict=1)
