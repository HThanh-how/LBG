from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    school_name = Column(String)
    
    classes = relationship("Class", back_populates="user")
    teaching_programs = relationship("TeachingProgram", back_populates="user")
    timetables = relationship("Timetable", back_populates="user")
    weekly_logs = relationship("WeeklyLog", back_populates="user")
    holidays = relationship("Holiday", back_populates="user")


class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_name = Column(String, nullable=False)
    grade = Column(String)
    school_year = Column(String)
    
    user = relationship("User", back_populates="classes")
    timetables = relationship("Timetable", back_populates="class_obj")
    teaching_programs = relationship("TeachingProgram", back_populates="class_obj")


class TeachingProgram(Base):
    __tablename__ = "teaching_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    subject_name = Column(String, nullable=False)
    lesson_index = Column(Integer, nullable=False)
    lesson_name = Column(String, nullable=False)
    
    user = relationship("User", back_populates="teaching_programs")
    class_obj = relationship("Class", back_populates="teaching_programs")


class Timetable(Base):
    __tablename__ = "timetables"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False)
    period_index = Column(Integer, nullable=False)
    subject_name = Column(String, nullable=False)
    
    user = relationship("User", back_populates="timetables")
    class_obj = relationship("Class", back_populates="timetables")


class WeeklyLog(Base):
    __tablename__ = "weekly_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    week_number = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    period_index = Column(Integer, nullable=False)
    subject_name = Column(String, nullable=False)
    lesson_name = Column(String, nullable=False)
    notes = Column(Text)
    
    user = relationship("User", back_populates="weekly_logs")


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    holiday_date = Column(Date, nullable=True)
    holiday_name = Column(String, nullable=False)
    is_moved = Column(Integer, default=0)
    moved_to_date = Column(Date, nullable=True)
    week_number = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_odd_day = Column(Integer, nullable=True)
    is_even_day = Column(Integer, nullable=True)

    user = relationship("User", back_populates="holidays")
