from app import app
from flask import render_template, jsonify, request, redirect, url_for
import logging
import base64
import json
from datetime import datetime
import pytz
from services.face_recognition_service import detect_faces

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Routes
@app.route("/")
def home():
    now = datetime.now()
    return render_template("index.html", now=now)

@app.route("/add-student")
def add_student_page():
    now = datetime.now()
    return render_template("add_student.html", now=now)

@app.route("/mark-attendance")
def mark_attendance_page():
    now = datetime.now()
    return render_template("mark_attendance.html", now=now)

@app.route("/attendance-log")
def attendance_log_page():
    now = datetime.now()
    return render_template("attendance_log.html", now=now)

@app.route("/admin-panel")
def admin_panel_page():
    now = datetime.now()
    return render_template("admin_panel.html", now=now)

# API Routes for Students
@app.route("/api/students/", methods=["GET"])
def get_all_students():
    from models import Student
    from app import db
    
    students = db.session.query(Student).all()
    return jsonify([{
        "id": student.id,
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "face_encoding": bool(student.face_encoding),  # Convert to boolean
        "created_at": student.created_at.isoformat() if student.created_at else None,
        "updated_at": student.updated_at.isoformat() if student.updated_at else None,
    } for student in students])

@app.route("/api/students/", methods=["POST"])
def create_student():
    from models import Student
    from app import db
    
    data = request.json
    student = Student(
        student_id=data["student_id"],
        name=data["name"],
        email=data["email"]
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({
        "id": student.id,
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "created_at": student.created_at.isoformat() if student.created_at else None,
        "updated_at": student.updated_at.isoformat() if student.updated_at else None,
    })

@app.route("/api/students/register-face", methods=["POST"])
def register_face():
    from models import Student
    from app import db
    from services.face_recognition_service import encode_face
    
    try:
        data = request.json
        student_id = data.get("student_id")
        image_data = base64.b64decode(data.get("image_data").split(',')[1])
        
        # Get real face encoding
        face_encoding = encode_face(image_data)
        if face_encoding is None:
            return jsonify({"success": False, "message": "No face detected in image"})
            
        # Update student with real face encoding
        student = db.session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        # Convert numpy array to list for JSON serialization
        student.face_encoding = json.dumps(face_encoding.tolist())
        db.session.commit()
        
        return jsonify({"success": True, "message": "Face registered successfully"})
        
    except Exception as e:
        logger.error(f"Error registering face: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    from models import Student
    from app import db
    
    try:
        # Find the student
        student = db.session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
            
        # Delete the student
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Student deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error deleting student: {str(e)}"
        }), 500

# API Routes for Attendance
@app.route("/api/attendance/mark", methods=["POST"])
def mark_attendance():
    from models import Student, Attendance
    from app import db
    from services.face_recognition_service import encode_face, compare_faces
    import json
    
    try:
        data = request.json
        image_data = base64.b64decode(data.get("image_data").split(',')[1])
        
        # Get face encoding from captured image
        face_encoding = encode_face(image_data)
        if face_encoding is None:
            return jsonify({"success": False, "message": "No face detected in image"})
        
        # Get all students
        students = db.session.query(Student).all()
        matched_student = None
        
        # Compare with stored face encodings
        for student in students:
            if not student.face_encoding:
                continue
                
            stored_encoding = json.loads(student.face_encoding)
            if compare_faces(face_encoding, stored_encoding):
                matched_student = student
                break
        
        if not matched_student:
            return jsonify({"success": False, "message": "Face not recognized"})
        
        # Mark attendance for matched student
        today = datetime.now().date()
        current_time = datetime.now(pytz.UTC)
        
        open_attendance = db.session.query(Attendance).filter(
            Attendance.student_id == matched_student.id,
            db.func.date(Attendance.check_in) == today,
            Attendance.check_out == None
        ).first()
        
        if open_attendance:
            # Check out
            open_attendance.check_out = current_time
            db.session.commit()
            return jsonify({
                "success": True,
                "student_id": matched_student.id,
                "name": matched_student.name,
                "message": f"Attendance check-out marked for {matched_student.name}"
            })
        else:
            # Check in
            new_attendance = Attendance(
                student_id=matched_student.id,
                check_in=current_time,
                status="present"
            )
            db.session.add(new_attendance)
            db.session.commit()
            return jsonify({
                "success": True,
                "student_id": matched_student.id,
                "name": matched_student.name,
                "message": f"Attendance check-in marked for {matched_student.name}"
            })
            
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        return jsonify({"success": False, "message": f"Error processing attendance: {str(e)}"})

@app.route("/api/attendance/", methods=["GET"])
def get_all_attendance():
    from models import Attendance, Student
    from app import db
    from sqlalchemy.orm import joinedload
    
    date_str = request.args.get("date")
    student_id = request.args.get("student_id")
    
    query = db.session.query(Attendance).options(joinedload(Attendance.student))
    
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Attendance.check_in) == filter_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    attendances = query.all()
    
    return jsonify([{
        "id": attendance.id,
        "student_id": attendance.student_id,
        "check_in": attendance.check_in.isoformat() if attendance.check_in else None,
        "check_out": attendance.check_out.isoformat() if attendance.check_out else None,
        "status": attendance.status,
        "created_at": attendance.created_at.isoformat() if attendance.created_at else None,
        "updated_at": attendance.updated_at.isoformat() if attendance.updated_at else None,
        "student": {
            "id": attendance.student.id,
            "student_id": attendance.student.student_id,
            "name": attendance.student.name,
            "email": attendance.student.email
        }
    } for attendance in attendances])

@app.route("/api/attendance/report/daily", methods=["GET"])
def get_daily_report():
    from models import Attendance, Student
    from app import db
    
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400
    
    try:
        filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get all students
    students = db.session.query(Student).all()
    
    report = []
    for student in students:
        # Find attendance for this student on the specified date
        attendance = db.session.query(Attendance).filter(
            Attendance.student_id == student.id,
            db.func.date(Attendance.check_in) == filter_date
        ).first()
        
        report.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "status": attendance.status if attendance else "absent",
            "check_in": attendance.check_in.isoformat() if attendance and attendance.check_in else None,
            "check_out": attendance.check_out.isoformat() if attendance and attendance.check_out else None
        })
    
    return jsonify(report)

@app.route("/api/detect-faces", methods=["POST"])
def detect_faces_endpoint():
    try:
        data = request.json
        image_data = base64.b64decode(data.get("image_data").split(',')[1])
        
        # Detect faces
        _, face_locations = detect_faces(image_data)
        
        return jsonify({
            "success": True,
            "faces": face_locations
        })
    except Exception as e:
        logger.error(f"Error detecting faces: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)