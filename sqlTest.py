from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError

# Define the database URL
DATABASE_URL = "sqlite:///courses.db"
# Create the engine
engine = create_engine(DATABASE_URL, echo=False)
# Define the base class for the ORM models
Base = declarative_base()

# Tables defined as python classes
class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    courses = relationship("Course", back_populates="instructor")

class Classroom(Base):
    __tablename__ = 'classroom'
    id = Column(Integer, primary_key=True)
    building = Column(String, nullable=False)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    max_enrollment = Column(Integer, nullable=False)
    instructor_id = Column(Integer, ForeignKey('faculty.id'))
    instructor = relationship("Faculty", back_populates="courses")
    classroom_id = Column(Integer, ForeignKey('classroom.id'))
    classroom = relationship("Classroom")


# Safe commit method for handling exceptions
def safe_commit(session):
    try:
        session.commit()
    except IntegrityError as e:
        print("*******")
        print(f"IntegrityError: {e}")
        print("*******")
        session.rollback()
    except Exception as e:
        print("*******")
        print(f"Error: {e}")
        print("*******")
        session.rollback()


# Create all tables in the database
Base.metadata.create_all(engine)


# Create a new session for adding entries
Session = sessionmaker(bind=engine)
session = Session()

# Add starter data
faculty_member = Faculty(id = 195, name="Dr. Smith", department="Computer Science")
classroom = Classroom(building="OKT", room_number="329", capacity=50)
course = Course(id = 115, name="Intro to Video Game Design", max_enrollment=50, instructor_id = 195, instructor=faculty_member, classroom=classroom)

session.add_all([faculty_member, classroom, course])
#session.commit()

# Use the safe_commit function
safe_commit(session)




# Query the data
courses = session.query(Course).all()
for course in courses:
    print(f"Course: {course.name}, Instructor: {course.instructor.name}, Classroom: {course.classroom.building} {course.classroom.room_number}")