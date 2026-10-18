EduManage – Student Management & Educational ERP System

EduManage is a full-stack Student Management and Educational ERP web application designed to help educational institutions manage student records, academics, attendance, examinations, and fee information through a centralized system.

The system replaces manual record management and disconnected spreadsheets with a structured relational database and a modern web-based interface.

🚀 Key Features

🔐 Authentication & Security

- Secure administrator login
- Password hashing using Werkzeug/PBKDF2
- Session-based authentication
- Protected routes using "@login_required"
- Change password functionality
- Server-side input validation
- Parameterized SQL queries for SQL injection prevention

📊 Dashboard

- Total students
- Active/inactive student statistics
- Total courses/programs
- Total subjects
- Institute-level marks statistics
- Student directory
- Real-time search without page reload

👨‍🎓 Student Management

- Add new students
- Edit student information
- Delete student records
- Active/Inactive status management
- Unique roll number validation
- Phone, semester and marks validation
- Personal and academic information management

📚 Course & Subject Management

- Create and manage courses
- Add and manage subjects
- Map subjects with courses and semesters
- Maintain structured academic curriculum

📅 Attendance Management

- Daily attendance recording
- Present / Absent / Late status
- Filter attendance by date, course and semester
- Automatic attendance percentage calculation
- Existing attendance records can be updated

📝 Examination & Marks

- Course and subject-wise marks entry
- Student examination records
- Automatic overall marks/average calculation
- Semester-wise academic information

💰 Fee Management

- Student fee records
- Total, paid and pending fee tracking
- Partial installment support
- Payment date and last payment details
- Financial summary dashboard

👤 360° Student Profile

A single student profile provides:

- Personal information
- Course and semester
- Attendance statistics
- Academic transcript
- Subject-wise marks
- Total/paid/pending fees

🛠️ Technology Stack

Technology| Purpose
Python 3.x| Backend programming & application logic
Flask| Web framework, routing and request handling
SQLite3| Relational database
HTML5| Web page structure
CSS3| Responsive UI and Glassmorphism design
JavaScript| DOM manipulation and live search
Jinja2| Dynamic server-side HTML rendering
Werkzeug| Password hashing and security
Boxicons| UI icons
ReportLab| PDF documentation/report generation

The project uses Flask for backend processing, SQLite for persistent relational data, Jinja2 for dynamic templates, and Vanilla CSS/JavaScript for the frontend.

🗄️ Database Design

The application uses a relational SQLite database with interconnected tables:

- "users"
- "students"
- "courses"
- "subjects"
- "attendance"
- "marks"
- "fees"

Foreign-key relationships are used to connect students with attendance, marks, subjects and fee records. Unique constraints are also implemented for important fields such as usernames, emails and student roll numbers.

🏗️ Architecture

The application follows an MVC/MTV-style architecture:

Browser → Flask Routes → Validation & Business Logic → SQLite Database → Jinja2 Templates → Browser

The main backend logic is handled through "app.py", while HTML templates are maintained inside the "templates/" directory and CSS/JavaScript files are stored inside "static/".

🔄 Data Flow

1. User sends a request from the browser.
2. Flask receives and processes the request.
3. Authentication and authorization are checked.
4. Server-side validation is performed.
5. Parameterized SQL queries interact with SQLite.
6. Database results are passed to Jinja2 templates.
7. HTML is dynamically rendered and returned to the browser.
8. JavaScript provides client-side features such as live search.

🔒 Security

Security and data integrity were considered during development:

- Password hashing
- Protected authentication routes
- Signed Flask sessions
- Parameterized SQL queries
- Server-side validation
- Unique roll-number enforcement
- Input range validation
- Flash messages for user feedback

📁 Main Project Structure

EduManage/
│
├── app.py
├── database.db
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── add_student.html
│   ├── edit_student.html
│   ├── attendance.html
│   ├── marks.html
│   ├── fees.html
│   ├── courses.html
│   └── subjects.html
│
└── static/
    ├── css/
    │   └── style.css
    └── Js/
        └── script.js

🎯 Project Objective

The primary objective of EduManage is to provide a centralized, secure and user-friendly platform for managing the complete student lifecycle — from admission and academic management to attendance, examinations and fee tracking.

🔮 Future Scope

Possible future improvements include:

- Student/Parent portal
- Email/SMS attendance notifications
- Excel/CSV bulk import and export
- Online fee payment using UPI/payment gateway
- Student fee receipt generation
- Role-based access for Admin, Teacher and Accountant
- Cloud deployment

📌 Project Status

Status: Completed / Operational
Project Type: Full-Stack Web ERP / Academic Management System
Version: 1.0.0

Skills Demonstrated

"Python" "Flask" "SQLite" "SQL" "HTML5" "CSS3" "JavaScript" "Jinja2" "CRUD" "REST-style Routing" "Authentication" "Database Design" "Input Validation" "Web Development" "Git/GitHub"# student-management-system