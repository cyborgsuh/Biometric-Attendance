import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Body, Form, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import base64

from database import get_db
import models
import schemas
from services.face_recognition_service import encode_face, compare_faces

router = APIRouter(prefix="/api/students", tags=["students"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.StudentResponse)
async def create_student(
    student: schemas.StudentCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new student with face encoding"""
    db_student = models.Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        face_encoding=student.face_encoding
    )
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.post("/register-face")
async def register_face(
    face_data: schemas.FaceData,
    student_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Register a face for a student"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(face_data.image_data.split(',')[1])
        
        # Generate face encoding
        face_encoding = encode_face(image_data)
        if face_encoding is None:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "No face detected in the image"}
            )
        
        # Store face encoding in the database
        student.face_encoding = json.dumps(face_encoding.tolist())
        db.commit()
        
        return JSONResponse(
            content={"success": True, "message": "Face registered successfully"}
        )
    except Exception as e:
        logger.error(f"Error registering face: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error registering face: {str(e)}"}
        )

@router.get("/", response_model=List[schemas.StudentResponse])
async def get_all_students(db: Session = Depends(get_db)):
    """Get all students"""
    students = db.query(models.Student).all()
    return students

@router.get("/{student_id}", response_model=schemas.StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a student by ID"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=schemas.StudentResponse)
async def update_student(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update a student"""
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update student fields if provided
    if student_update.student_id is not None:
        db_student.student_id = student_update.student_id
    if student_update.name is not None:
        db_student.name = student_update.name
    if student_update.email is not None:
        db_student.email = student_update.email
    if student_update.face_encoding is not None:
        db_student.face_encoding = student_update.face_encoding
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student"""
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}
