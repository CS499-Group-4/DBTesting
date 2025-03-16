from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from lib.DatabaseManager import DatabaseManager, Faculty, Course, TimeSlot, Schedule, Classroom  # Assuming database_manager.py contains the schema

import logging

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
    
    def get_preferred_slots(self, professor):
        all_slots = self.session.query(TimeSlot).all() #Get all timeslots
        available_slots = []

        # For profs with preference
        if professor.Preference != "None":
            if "Morning" in professor.Preference:
                if "Mon-Weds" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime < "12:00" and slot.Days == "MW"]
                elif "Tues-Thurs" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime < "12:00" and slot.Days == "TR"]
                else:
                    available_slots += [slot for slot in all_slots if slot.StartTime < "12:00"]
            if "Afternoon" in professor.Preference:
                if "Mon-Weds" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "12:00" and slot.StartTime < "17:00" and slot.Days == "MW"]
                elif "Tues-Thurs" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "12:00" and slot.StartTime < "17:00" and slot.Days == "TR"]
                else:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "12:00" and slot.StartTime < "17:00"]
            if "Evening" in professor.Preference:
                if "Mon-Weds" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "17:00" and slot.Days == "MW"]
                elif "Tues-Thurs" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "17:00" and slot.Days == "TR"]
                else:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "17:00"]
            if ("Morning" or "Afternoon" or "Evening") not in professor.Preference:
                if "Mon-Weds" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.Days == "MW"]
                elif "Tues-Thurs" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.Days == "TR"]
            
        else:
            available_slots = all_slots

        # Remove slots where professor is already scheduled
        for slot in available_slots:
                if self.is_professor_occupied(professor, slot):
                    available_slots.remove(slot)

        return available_slots
    

    
    # Return bool if professor is scheduled for given timeslot
    def is_professor_occupied(self, professor, timeslot):
        
        return self.session.query(Schedule).filter(
            and_(Schedule.Professor == professor.FacultyID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0
    
    # Return bool if room is occupied at given time already
    def is_room_occupied(self, room, timeslot):
        
        return self.session.query(Schedule).filter(
            and_(Schedule.Classroom == room.RoomID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0
    
    
    def get_professor_availability(self, professor):
        # Get all timeslots
        available_slots = self.session.query(TimeSlot).all()

        for slot in available_slots:
                if self.is_professor_occupied(professor, slot):
                    available_slots.remove(slot)

        return available_slots
    

    def get_prof_slots(self, professor):
        preferred_timeslots = self.get_preferred_slots(professor)
        prof_all_slots = self.get_professor_availability(professor)

        return preferred_timeslots, prof_all_slots


    # def assign_room(self, course, professor):
    #     prof_all_slots = self.get_professor_availability(professor)

    #     # Check all the prof's preferred timeslots
    #     for slot in self.get_preferred_slots(professor):
    #         # Assign the required room if it's available
    #         if course.ReqRoom:
    #             if not self.is_room_occupied(course.ReqRoom, slot):
    #                 return course.ReqRoom
    #         else:
    #             for room in self.session.query(Classroom).all():
    #                 if not self.is_room_occupied(room.RoomID, slot):
    #                     return room.RoomID
                



    #     # Otherwise, pick the first available room
    #     available_rooms = self.session.query(Classroom).all()
    #     for room in available_rooms:
    #         if not self.is_room_occupied(room.RoomID, slot):
    #             return room.RoomID

    #     return None

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    scheduler = CourseScheduler()
    #scheduler.generate_schedule()

    #Sort courses by professor preference / courses with req. classroom
    sorted_courses = scheduler.get_sorted_courses(scheduler.session)
    all_faculty = scheduler.db.get_faculty()
    
    #To store schedule info before committing to the schedule table
    final_timeslot = None
    final_room = None


    #Go course-by-course
    for course in sorted_courses:
        logging.debug(f"CourseID: {course.CourseID}, Required Room: {course.ReqRoom}")
        #For each professor to teach this course (can be removed if only one professor per course)
        for professor in (p for p in all_faculty if course.CourseID in (p.Class1, p.Class2, p.Class3)):
            preferred_timeslots, all_timeslots = scheduler.get_prof_slots(professor)
            
            #If required room 
            #Find a timeslot where the required room is available
            if course.ReqRoom:
                final_room = course.ReqRoom
                for slot in preferred_timeslots:
                    if not scheduler.is_room_occupied(course.ReqRoom, slot):
                        final_timeslot = slot
                        break
                #Conflict: Couldn't get preferred timeslot with required room
                if not final_timeslot:
                    for slot in all_timeslots:
                        if not scheduler.is_room_occupied(course.ReqRoom, slot):
                            final_timeslot = slot
                            break
                #Conflict: Couldn't get any timeslot with required room
            #Else no required room
            #Find a timeslot where any room is available
            else:
                for slot in preferred_timeslots:
                    for room in scheduler.db.get_classrooms():
                        if not scheduler.is_room_occupied(room, slot):
                            final_room = room
                            final_timeslot = slot
                            break
                #Conflict: Couldn't get preferred timeslot with any room
                if not final_timeslot:
                    for slot in all_timeslots:
                        for room in scheduler.db.get_classrooms():
                            if not scheduler.is_room_occupied(room, slot):
                                final_room = room
                                final_timeslot = slot
                                break
                #Conflict: Couldn't get any timeslot with any room

            #Commit to schedule table
            scheduler.db.add_schedule(final_timeslot, professor, course, final_room)
            logging.debug(f"ASSIGNED: CourseID: {course.CourseID}, Professor: {professor.Name}, Timeslot: {final_timeslot.Days} {final_timeslot.StartTime}, Room: {final_room.RoomID}")

            




    # for professor in all_faculty:
    #     potential_timeslots = scheduler.get_potential_timeslots(professor)
    #     print(f"{professor.Name} ({professor.Preference}) can teach at the following times:")
    #     for slot in potential_timeslots:
    #         print(f"{slot.Days} {slot.StartTime}")
        

    #Print all timeslots from the timeslot relation
    # timeslots = scheduler.db.get_timeslot()
    # print(f"SlotID\tDays\tTime")
    # for timeslot in timeslots:
    #     print(f"{timeslot.SlotID}\t{timeslot.Days}\t{timeslot.StartTime}")