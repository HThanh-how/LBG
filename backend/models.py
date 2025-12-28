from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    school_name = Column(String)
    
    teaching_programs = relationship("TeachingProgram", back_populates="user")
    timetables = relationship("Timetable", back_populates="user")
    weekly_logs = relationship("WeeklyLog", back_populates="user")


class TeachingProgram(Base):
    __tablename__ = "teaching_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_name = Column(String, nullable=False)
    lesson_index = Column(Integer, nullable=False)
    lesson_name = Column(String, nullable=False)
    
    user = relationship("User", back_populates="teaching_programs")


class Timetable(Base):
    __tablename__ = "timetables"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    period_index = Column(Integer, nullable=False)
    subject_name = Column(String, nullable=False)
    
    user = relationship("User", back_populates="timetables")


class WeeklyLog(Base):
    __tablename__ = "weekly_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    period_index = Column(Integer, nullable=False)
    subject_name = Column(String, nullable=False)
    lesson_name = Column(String, nullable=False)
    notes = Column(Text)
    
    user = relationship("User", back_populates="weekly_logs")

