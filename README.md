# Biometric Attendance

A modern face recognition-based attendance system built with Flask, OpenCV, and deep learning. This system provides an efficient, contactless way to track student attendance using facial biometrics.

## Features

- 👤 Face Recognition-based attendance marking
- 📝 Student registration with facial data
- 📊 Real-time attendance tracking
- 📈 Comprehensive attendance reports
- 🎛️ Admin panel for system management
- 📱 Responsive web interface
- 🔒 Secure and contactless attendance marking

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Face Recognition**: OpenCV, face_recognition library
- **ORM**: SQLAlchemy
- **Template Engine**: Jinja2

## Prerequisites

- Python 3.11 or higher
- MySQL Server
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git https://github.com/cyborgsuh/Biometric-Attendance
cd SmartAttendanceTracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the MySQL database:
- Create a new database named `attendance_system`
- Update the database connection string in `app.py`:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://username:password@localhost/attendance_system"
```

5. Initialize the database:
```bash
flask db upgrade
```

## Configuration

1. Environment Variables (create a `.env` file):
```env
SESSION_SECRET=your_secret_key
DATABASE_URL=mysql+pymysql://username:password@localhost/attendance_system
```

2. Adjust face recognition settings in `services/face_recognition_service.py` if needed.

## Running the Application

1. Start the Flask development server:
```bash
python main.py
```

2. Access the application at `http://localhost:5000`

## Usage

### 1. Student Registration
- Navigate to "Register Student"
- Fill in student details
- Capture student's face image
- Submit registration

### 2. Mark Attendance
- Go to "Mark Attendance"
- Allow camera access
- Student faces will be automatically recognized
- Attendance is marked in real-time

### 3. View Reports
- Access "Attendance Logs"
- Filter by date or student
- Export reports in CSV format
- Print attendance reports

### 4. Admin Panel
- Manage students
- View attendance statistics
- Configure system settings
- Generate comprehensive reports

## Project Structure

```
SmartAttendanceTracker/
├── services/
│   └── face_recognition_service.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_student.html
│   ├── mark_attendance.html
│   ├── attendance_log.html
│   └── admin_panel.html
├── app.py
├── main.py
├── models.py
└── database.py
```

## Security Features

- Face recognition with adjustable tolerance
- Secure database connections
- Input validation and sanitization
- Session management
- Error logging and handling

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV team for computer vision capabilities
- face_recognition library contributors
- Flask and SQLAlchemy communities
- Bootstrap team for the responsive UI framework

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.