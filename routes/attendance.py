import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import base64
from datetime import datetime
import pytz

from database import get_db
import models
import schemas
from services.face_recognition_service import compare_faces, encode_face

router = APIRouter(prefix="/api/attendance", tags=["attendance"])
logger = logging.getLogger(__name__)

@router.post("/mark", response_model=schemas.FaceRecognitionResponse)
async def mark_attendance(
    face_data: schemas.FaceData,
    db: Session = Depends(get_db)
):
    """Mark attendance using face recognition"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(face_data.image_data.split(',')[1])
        
        # Generate face encoding for the captured image
        face_encoding = encode_face(image_data)
        if face_encoding is None:
            return {
                "success": False,
                "message": "No face detected in the image"
            }
        
        # Get all students from the database
        students = db.query(models.Student).all()
        
        # Find matching student
        for student in students:
            if not student.face_encoding:
                continue
            
            # Parse stored face encoding from JSON string to list
            stored_encoding = json.loads(student.face_encoding)
            
            # Compare faces
            if compare_faces(face_encoding, stored_encoding):
                # Check if there's an open attendance record (with check_in but no check_out)
                today = datetime.now().date()
                open_attendance = db.query(models.Attendance).filter(
                    models.Attendance.student_id == student.id,
                    models.Attendance.check_in >= today,
                    models.Attendance.check_out.is_(None)
                ).first()
                
                current_time = datetime.now(pytz.UTC)
                
                if open_attendance:
                    # Check out
                    open_attendance.check_out = current_time
                    db.commit()
                    return {
                        "success": True,
                        "student_id": student.id,
                        "name": student.name,
                        "message": f"Attendance check-out marked for {student.name}"
                    }
                else:
                    # Check in
                    new_attendance = models.Attendance(
                        student_id=student.id,
                        check_in=current_time,
                        status="present"
                    )
                    db.add(new_attendance)
                    db.commit()
                    return {
                        "success": True,
                        "student_id": student.id,
                        "name": student.name,
                        "message": f"Attendance check-in marked for {student.name}"
                    }
        
        # No matching student found
        return {
            "success": False,
            "message": "Face not recognized. Please register first."
        }
    
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing attendance: {str(e)}"
        }

@router.get("/", response_model=List[schemas.AttendanceResponse])
async def get_all_attendance(
    db: Session = Depends(get_db),
    date: Optional[str] = None,
    student_id: Optional[int] = None
):
    """Get all attendance records with optional date and student filter"""
    query = db.query(models.Attendance)
    
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(db.func.date(models.Attendance.check_in) == filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    
    attendances = query.all()
    return attendances

@router.get("/{attendance_id}", response_model=schemas.AttendanceResponse)
async def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Get an attendance record by ID"""
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance

@router.put("/{attendance_id}", response_model=schemas.AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_update: schemas.AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """Update an attendance record"""
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    if attendance_update.status is not None:
        attendance.status = attendance_update.status
    if attendance_update.check_out is not None:
        attendance.check_out = attendance_update.check_out
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Delete an attendance record"""
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance record deleted successfully"}

@router.get("/report/daily", response_model=List[dict])
async def get_daily_report(date: str, db: Session = Depends(get_db)):
    """Get daily attendance report for a specific date"""
    try:
        filter_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get all students
    students = db.query(models.Student).all()
    
    report = []
    for student in students:
        # Find attendance for this student on the specified date
        attendance = db.query(models.Attendance).filter(
            models.Attendance.student_id == student.id,
            db.func.date(models.Attendance.check_in) == filter_date
        ).first()
        
        report.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "status": attendance.status if attendance else "absent",
            "check_in": attendance.check_in if attendance else None,
            "check_out": attendance.check_out if attendance else None
        })
    
    return report
