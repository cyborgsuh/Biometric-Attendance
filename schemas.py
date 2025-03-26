from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Student schemas
class StudentBase(BaseModel):
    student_id: str
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    face_encoding: Optional[str] = None

class StudentUpdate(BaseModel):
    student_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    face_encoding: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Attendance schemas
class AttendanceBase(BaseModel):
    student_id: int
    status: str = "present"

class AttendanceCreate(AttendanceBase):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    check_out: Optional[datetime] = None

class AttendanceResponse(AttendanceBase):
    id: int
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    student: StudentResponse

    class Config:
        orm_mode = True

# Face recognition schemas
class FaceData(BaseModel):
    image_data: str  # Base64 encoded image

class FaceRecognitionResponse(BaseModel):
    success: bool
    student_id: Optional[int] = None
    name: Optional[str] = None
    message: str
