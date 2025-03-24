from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from lib.DatabaseManager import DatabaseManager, Faculty, Course, TimeSlot, Schedule, Classroom  # Assuming database_manager.py contains the schema

import logging

class CourseScheduler:
    def __init__(self, db_url="sqlite:///course.db"):
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
        #all_slots should be an array of each timeslot objects timeslot.SlotID
        available_slots = []

        # For profs with preference
        if professor.Preference != "None":
            if "Morning" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime < "12:00"]
            elif "Afternoon" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "12:00" and slot.StartTime < "17:00"]
            elif "Evening" in professor.Preference:
                    available_slots += [slot for slot in all_slots if slot.StartTime >= "17:00"]
            
            if "Mon-Wed" in professor.Preference:
                available_slots += [slot for slot in all_slots if slot.Days == "MW"]
            elif "Tues-Thurs" in professor.Preference:
                available_slots += [slot for slot in all_slots if slot.Days == "TR"]
        else:
            available_slots = all_slots
        
        #Remove slots where professor is already scheduled
        filtered_slots = []
        for slot in available_slots:
            if self.is_professor_occupied(professor, slot):
                pass
                #print("REMOVING: Professor ", professor.FacultyID, " is already scheduled for ", slot.SlotID)
            else:
                filtered_slots.append(slot)

        available_slots = filtered_slots

        return available_slots
    

    
    # Return bool if professor is scheduled for given timeslot
    def is_professor_occupied(self, professor, timeslot):
        if self.session.query(Schedule).filter(
            and_(Schedule.Professor == professor.FacultyID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0:
            #print("OCCUPIED: Professor ", professor.FacultyID, " is already scheduled for ", timeslot.SlotID)
            return True
        #print("NOT OCCUPIED: Professor ", professor.FacultyID, " is not scheduled for ", timeslot.SlotID)
        return False
        return self.session.query(Schedule).filter(
            and_(Schedule.Professor == professor.FacultyID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0
    
    # Return bool if room is occupied at given time already
    def is_room_occupied(self, room, timeslot):
        
        return self.session.query(Schedule).filter(
            and_(Schedule.Classroom == room.RoomID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0
    
    
    # Return bool if room is occupied at given time already
    def is_roomID_occupied(self, roomID, timeslot):
        room = self.session.query(Classroom).filter(Classroom.RoomID == roomID)
        room = room[0]

        return self.session.query(Schedule).filter(
            and_(Schedule.Classroom == room.RoomID, Schedule.TimeSlot == timeslot.SlotID)).count() > 0
    

    
    
    # def get_professor_availability(self, professor):
    #     # Get all timeslots
    #     available_slots = self.session.query(TimeSlot).all()

    #     for slot in available_slots:
    #         if self.is_professor_occupied(professor, slot):
    #             available_slots.remove(slot)

    #     return available_slots
    

    def get_prof_slots(self, professor):
        preferred_timeslots = self.get_preferred_slots(professor)
        #prof_all_slots = self.get_professor_availability(professor)

        return preferred_timeslots#, prof_all_slots


    def conflict_scan(self):
        #For each professor and timeslot, check if they appear as a pair more than once
        for slot in self.session.query(TimeSlot).all():
            for prof in self.session.query(Faculty).all():
                if self.session.query(Schedule).filter(and_(Schedule.Professor == prof.FacultyID, Schedule.TimeSlot == slot.SlotID)).count() > 1:
                    print(f"CONFLICT: Professor {prof.FacultyID} is scheduled for {slot.SlotID} more than once")
            for room in self.session.query(Classroom).all():
                if self.session.query(Schedule).filter(and_(Schedule.Classroom == room.RoomID, Schedule.TimeSlot == slot.SlotID)).count() > 1:
                    print(f"CONFLICT: Room {room.RoomID} is scheduled for {slot.SlotID} more than once")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    scheduler = CourseScheduler()
    #scheduler.generate_schedule()

    # #Sort courses by professor preference / courses with req. classroom
    # sorted_courses = scheduler.get_sorted_courses(scheduler.session)
    # all_faculty = scheduler.db.get_faculty()
    
    # #To store schedule info before committing to the schedule table
    # final_timeslot = None
    # final_room = None


    # #Go course-by-course
    # for course in sorted_courses:
    #     print(f"Scheduling: CourseID: {course.CourseID}, Required Room: {course.ReqRoom}")
    #     #For each professor to teach this course (can be removed if only one professor per course)
    #     for professor in (p for p in all_faculty if course.CourseID in (p.Class1, p.Class2, p.Class3)):
    #         #print("Getting prof slots")
    #         preferred_timeslots = scheduler.get_prof_slots(professor)
            
    #         #If required room 
    #         #Find a timeslot where the required room is available
    #         if course.ReqRoom != None:
    #             final_room = scheduler.session.query(Classroom).filter(Classroom.RoomID == course.ReqRoom)
                
    #             if final_room.count() == 0:
    #                 print(f"ERROR: Required room {course.ReqRoom} not found in database")
    #                 continue
    #             final_room = final_room[0]

    #             for slot in preferred_timeslots:
    #                 if not scheduler.is_room_occupied(final_room, slot):
    #                     final_timeslot = slot
    #                     break
    #             #Conflict: Couldn't get preferred timeslot with required room
    #             if not final_timeslot:
    #                 print("COULDN'T GET PREFERRED TIMESLOT WITH REQUIRED ROOM")
    #                 for slot in scheduler.session.query(TimeSlot).all():
    #                     if not scheduler.is_room_occupied(final_room, slot) and not scheduler.is_professor_occupied(professor, slot):
    #                         final_timeslot = slot
    #                         break
    #             #Conflict: Couldn't get any timeslot with required room
    #         #Else no required room
    #         #Find a timeslot where any room is available
    #         else:
    #             for slot in preferred_timeslots:
    #                 for room in scheduler.db.get_classrooms():
    #                     if not scheduler.is_room_occupied(room, slot):
    #                         final_room = room
    #                         final_timeslot = slot
    #                         break
    #             #Conflict: Couldn't get preferred timeslot with any room
    #             if not final_timeslot:
    #                 for slot in scheduler.session.query(TimeSlot).all():
    #                     for room in scheduler.db.get_classrooms():
    #                         if not scheduler.is_room_occupied(room, slot):
    #                             final_room = room
    #                             final_timeslot = slot
    #                             break
    #             #Conflict: Couldn't get any timeslot with any room

    #         #Commit to schedule table
    #         scheduler.db.add_schedule(final_timeslot, professor, course, final_room)
    #         print(f"ASSIGNED: CourseID: {course.CourseID}, Professor: {professor.Name}, Timeslot: {final_timeslot.Days} {final_timeslot.StartTime}, Room: {final_room.RoomID}")
    
    # #Add course CS 659 to courses
    # scheduler.db.add_course("CS 659", None)
    # #Add course CS 601 to courses
    # scheduler.db.add_course("CS 601", None)
    # #Add Room OKT659 to classrooms
    # scheduler.db.add_classroom("OKT659", "OKT", 659)

    
    
    # scheduler.db.DEBUG_add_schedule_manual(1, 9, "CS 659", "OKT659")#Double book professor conflict
    # scheduler.db.DEBUG_add_schedule_manual(1, 11, "CS 601", "OKT131")#Double book room conflict
    print("Running conflict scan")
    scheduler.conflict_scan()
    print("Conflict scan complete")
