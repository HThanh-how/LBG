from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserBase(BaseModel):
    username: str
    full_name: str
    school_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TeachingProgramBase(BaseModel):
    subject_name: str
    lesson_index: int
    lesson_name: str


class TeachingProgramCreate(TeachingProgramBase):
    pass


class TeachingProgramResponse(TeachingProgramBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class TimetableBase(BaseModel):
    day_of_week: int
    period_index: int
    subject_name: str


class TimetableCreate(TimetableBase):
    pass


class TimetableResponse(TimetableBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class WeeklyLogBase(BaseModel):
    week_number: int
    day_of_week: int
    period_index: int
    subject_name: str
    lesson_name: str
    notes: Optional[str] = None


class WeeklyLogCreate(WeeklyLogBase):
    pass


class WeeklyLogResponse(WeeklyLogBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

