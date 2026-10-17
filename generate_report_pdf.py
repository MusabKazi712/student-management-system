import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Don't draw running header on cover page (page 1)
        if self._pageNumber > 1:
            # Running Header
            self.drawString(54, 802, "EduManage - Student Management System | Complete Technical Project Documentation")
            self.drawRightString(541, 802, "Flask, SQLite & Modern UI")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, 794, 541, 794)

        # Running Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 45, 541, 45)
        
        self.drawString(54, 32, "EduManage Academic Project Report | Confidential & Educational Use Only")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 32, page_str)
        self.restoreState()


def generate_pdf(filename="Student_Management_System_Project_Report.pdf"):
    # Page dimensions for A4: 595.27 x 841.89 points
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Color Palette
    primary = colors.HexColor("#1E3A8A")    # Deep Navy Blue
    secondary = colors.HexColor("#0D9488")  # Teal Accent
    accent = colors.HexColor("#4F46E5")     # Indigo
    dark_text = colors.HexColor("#1E293B")  # Slate 800
    muted_text = colors.HexColor("#475569") # Slate 600
    card_bg = colors.HexColor("#F8FAFC")    # Slate 50
    border_col = colors.HexColor("#E2E8F0") # Subtle Border

    # Styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary,
        alignment=0,
        spaceAfter=6
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=dark_text,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=dark_text,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.2,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    th_style = ParagraphStyle(
        'TH_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TD_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=dark_text
    )

    td_bold = ParagraphStyle(
        'TDBold_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.2,
        textColor=dark_text
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    
    badge_data = [[
        Paragraph("<b>ACADEMIC & INDUSTRY PROJECT REPORT</b>", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#0284C7"))),
        Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", ParagraphStyle('DateBadge', fontName='Helvetica', fontSize=8.5, alignment=2, textColor=muted_text))
    ]]
    t_badge = Table(badge_data, colWidths=[330, 157])
    t_badge.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_badge)
    story.append(Spacer(1, 10))

    story.append(Paragraph("EduManage", cover_title_style))
    story.append(Paragraph("Complete Student Management & Educational ERP System", cover_subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=primary, spaceAfter=14))

    story.append(Paragraph(
        "<b>Executive Project Summary:</b><br/>"
        "Yeh document <b>EduManage (Student Management System)</b> ka complete technical, architectural aur operational report hai. "
        "Isme explain kiya gaya hai ki is project me <b>kya-kya banaya gaya</b>, <b>kaun-kaun si technologies use hui</b>, "
        "<b>system kaise build kiya gaya</b>, database schema aur data models kaise connect hain, aur internal data flow "
        "browser se lekar database tak kaise execute hota hai.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Cover Summary Box
    summary_box_data = [
        [
            Paragraph("<b>Project Category</b>", td_bold),
            Paragraph("Full-Stack Web ERP / Academic Institutional System", td_style)
        ],
        [
            Paragraph("<b>Backend Core</b>", td_bold),
            Paragraph("Python 3.x, Flask Web Framework (WSGI, Jinja2, Werkzeug)", td_style)
        ],
        [
            Paragraph("<b>Database</b>", td_bold),
            Paragraph("SQLite3 (Embedded Relational DB, 7 Interlinked Tables)", td_style)
        ],
        [
            Paragraph("<b>Frontend UI/UX</b>", td_bold),
            Paragraph("HTML5, Vanilla CSS3 (Custom Glassmorphism), JavaScript (DOM Live Search)", td_style)
        ],
        [
            Paragraph("<b>Security & Auth</b>", td_bold),
            Paragraph("PBKDF2 Password Hashing, Session Security, @login_required Route Decorator", td_style)
        ],
        [
            Paragraph("<b>Modules Built</b>", td_bold),
            Paragraph("Auth & Passwords, KPI Dashboard, Student CRUD, Courses, Subjects, Attendance, Exams/Marks, Fees, 360° Profile", td_style)
        ],
        [
            Paragraph("<b>Project Status</b>", td_bold),
            Paragraph("<font color='#0D9488'><b>100% Operational & Production Ready (Phase 4 Completed)</b></font>", td_style)
        ]
    ]
    t_sum_box = Table(summary_box_data, colWidths=[120, 367])
    t_sum_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), card_bg),
        ('BOX', (0,0), (-1,-1), 1.2, primary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum_box)
    story.append(Spacer(1, 14))

    # Table of contents index box
    story.append(Paragraph("<b>Table of Contents / Report Index:</b>", h2_style))
    toc_data = [
        [Paragraph("1. Project Overview & Core Objectives", td_style), Paragraph("6. Data Flow & Request Processing Lifecycle", td_style)],
        [Paragraph("2. Technology Stack & Tools Used", td_style), Paragraph("7. Security & Input Validation Safeguards", td_style)],
        [Paragraph("3. System Architecture & Project Structure", td_style), Paragraph("8. How to Setup & Run the Application", td_style)],
        [Paragraph("4. Relational Database Design & Schema", td_style), Paragraph("9. Future Scope & Conclusion", td_style)],
        [Paragraph("5. Detailed Modules & Implemented Features", td_style), Paragraph("Appendix: Source Code & File Inventory", td_style)]
    ]
    t_toc = Table(toc_data, colWidths=[243, 244])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_toc)

    # Clean PageBreak after cover
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: OVERVIEW & OBJECTIVES
    # =========================================================================
    story.append(Paragraph("1. Executive Project Overview (प्रोजेक्ट का परिचय और उद्देश्य)", h1_style))
    story.append(Paragraph(
        "<b>EduManage</b> ek full-fledged, modular aur secure <b>Student Management Web Application</b> hai. "
        "Educational institutions (jaise colleges, institutes, aur schools) me student records ko maintain karne ke liye "
        "pehle manual files, physical registers ya disconnected Excel spreadsheets use hoti thi. Isse human errors, duplicate roll numbers, "
        "attendance register gum hone, aur fee dues miss hone ki badi samasya aati thi. "
        "Is project ko ek comprehensive, single-source-of-truth ke roop me build kiya gaya hai jo student life-cycle ke sabhi stages "
        "(Admission -> Course/Subject Mapping -> Daily Attendance -> Examination Marks -> Fee Collection -> Academic Transcript) ko automate karta hai.",
        body_style
    ))
    story.append(Paragraph("<b>Mukhya Lakshya (Key Objectives):</b>", td_bold))
    story.append(Paragraph("• <b>Centralized Student Repository:</b> Sabhi students ka personal, contact aur academic record ek structured database me secure rakhna.", bullet_style))
    story.append(Paragraph("• <b>Integrity & Zero Duplication:</b> Unique roll numbers enforce karna taaki duplicate admission bilkul na ho sake.", bullet_style))
    story.append(Paragraph("• <b>Daily Attendance Automation:</b> Single-click interface se daily attendance record karna aur percentage automatically calculate karna.", bullet_style))
    story.append(Paragraph("• <b>Examination Automation:</b> Subject-wise marks save hote hi overall aggregate percentage automatic recalculate hona.", bullet_style))
    story.append(Paragraph("• <b>Financial Accountability:</b> Transparent fee collection ledger maintain karna jisme total fee, paid amount aur pending balance real-time track ho.", bullet_style))
    story.append(Paragraph("• <b>Access Security:</b> Hashed passwords aur session protection ke zariye administrative data ko unauthorized access se bachana.", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("2. Technology Stack & Tools Used (कौन-कौन सी टेक्नोलॉजीज इस्तेमाल हुईं)", h1_style))
    story.append(Paragraph(
        "Project ko lightweight, fast, modern aur production-ready banane ke liye standard open-source technologies ka use kiya gaya hai:",
        body_style
    ))

    tech_table_data = [
        [Paragraph("Layer", th_style), Paragraph("Technology / Tool", th_style), Paragraph("Role & Implementation Details", th_style)],
        [
            Paragraph("<b>Backend Core</b>", td_bold),
            Paragraph("<b>Python 3.x</b>", td_style),
            Paragraph("Core programming language; application logic, business rules, mathematical formulas, aur SQLite connectivity handle karta hai.", td_style)
        ],
        [
            Paragraph("<b>Web Framework</b>", td_bold),
            Paragraph("<b>Flask 3.x</b>", td_style),
            Paragraph("Micro web framework jo HTTP routes, request processing, sessions, URL dispatching, aur Jinja2 template rendering handle karta hai.", td_style)
        ],
        [
            Paragraph("<b>Database</b>", td_bold),
            Paragraph("<b>SQLite 3</b>", td_style),
            Paragraph("Serverless, zero-configuration relational database (<code>database.db</code>). Relational foreign keys, ACID compliance aur instant queries provide karta hai.", td_style)
        ],
        [
            Paragraph("<b>Template Engine</b>", td_bold),
            Paragraph("<b>Jinja 2</b>", td_style),
            Paragraph("Dynamic server-side templating; master template inheritance (<code>base.html</code>), conditional statements, loops aur context passing provide karta hai.", td_style)
        ],
        [
            Paragraph("<b>Frontend Styling</b>", td_bold),
            Paragraph("<b>Vanilla CSS3</b>", td_style),
            Paragraph("Custom Glassmorphism UI tokens, frosted glass cards (<code>backdrop-filter</code>), modern color variables, CSS Grid aur Flexbox layouts.", td_style)
        ],
        [
            Paragraph("<b>Client Scripting</b>", td_bold),
            Paragraph("<b>Vanilla JavaScript</b>", td_style),
            Paragraph("DOM manipulation aur event listeners for real-time table filtering without page reloads.", td_style)
        ],
        [
            Paragraph("<b>Security & Auth</b>", td_bold),
            Paragraph("<b>Werkzeug Security</b>", td_style),
            Paragraph("Cryptographic PBKDF2/scrypt password hashing (<code>generate_password_hash</code>, <code>check_password_hash</code>) aur signed cookie sessions.", td_style)
        ],
        [
            Paragraph("<b>Icons UI</b>", td_bold),
            Paragraph("<b>Boxicons CDN</b>", td_style),
            Paragraph("Vector icons for sidebar navigation, KPI cards, student actions, and status badges.", td_style)
        ],
        [
            Paragraph("<b>Report Engine</b>", td_bold),
            Paragraph("<b>ReportLab 5.x</b>", td_style),
            Paragraph("Programmatic PDF generation engine used to compile this executive-grade documentation.", td_style)
        ]
    ]

    t_tech = Table(tech_table_data, colWidths=[90, 115, 282])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 3: SYSTEM ARCHITECTURE & FILE DIRECTORY
    # =========================================================================
    story.append(Paragraph("3. System Architecture & Design Pattern (सिस्टम कैसे बनाया गया)", h1_style))
    story.append(Paragraph(
        "Is system ko <b>MVC (Model-View-Controller) / MTV (Model-Template-View)</b> architectural pattern par develop kiya gaya hai:",
        body_style
    ))
    story.append(Paragraph("• <b>Model (Data Layer):</b> SQLite3 tables (<code>students</code>, <code>courses</code>, <code>subjects</code>, <code>attendance</code>, <code>marks</code>, <code>fees</code>, <code>users</code>) jisme data constraints, primary keys aur foreign key relationships enforce hain.", bullet_style))
    story.append(Paragraph("• <b>Controller / View (Business Logic Layer):</b> <code>app.py</code> me Flask route handlers aur Python logic jo request validation, authorization checks, calculations (attendance %, pending balance, student GPA average) aur database queries execute karte hain.", bullet_style))
    story.append(Paragraph("• <b>Template (Presentation Layer):</b> <code>templates/</code> directory me Jinja2 templates (jaise <code>base.html</code>) jo dynamic HTML render karte hain, aur <code>static/</code> directory me CSS styling aur JS behaviors hain.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Project File Structure & Roles (फाइल संरचना):</b>", h2_style))
    fs_data = [
        [Paragraph("File / Folder", th_style), Paragraph("Role & Description", th_style)],
        [Paragraph("<b>app.py</b>", code_style), Paragraph("Main application backend: Flask app setup, DB connection, @login_required decorator, and 15+ HTTP routes.", td_style)],
        [Paragraph("<b>database.db</b>", code_style), Paragraph("SQLite database storing persistent records (students, courses, subjects, attendance, marks, fees, users).", td_style)],
        [Paragraph("<b>templates/base.html</b>", code_style), Paragraph("Master layout with glassmorphic sidebar, top notification banners, session user badge, and block contents.", td_style)],
        [Paragraph("<b>templates/index.html</b>", code_style), Paragraph("Institute dashboard with KPI stat cards, student table directory, and real-time live search.", td_style)],
        [Paragraph("<b>templates/profile.html</b>", code_style), Paragraph("360-degree comprehensive student profile aggregating attendance stats, marksheet, and fee ledger.", td_style)],
        [Paragraph("<b>templates/login.html</b>", code_style), Paragraph("Secure administrative login interface with credentials verification and error feedback.", td_style)],
        [Paragraph("<b>templates/add_student.html</b><br/><b>templates/edit_student.html</b>", code_style), Paragraph("Student admission and update forms with strict server-side validation (phone, unique roll no, semester, marks).", td_style)],
        [Paragraph("<b>templates/attendance.html</b>", code_style), Paragraph("Daily attendance marking portal with date/course/sem filters and daily attendance percentage metrics.", td_style)],
        [Paragraph("<b>templates/marks.html</b>", code_style), Paragraph("Examination marks entry sheet with automatic live recalculation of student's overall aggregate score.", td_style)],
        [Paragraph("<b>templates/fees.html</b>", code_style), Paragraph("Fee collection accounting dashboard with payment installments, pending dues, and financial summary cards.", td_style)],
        [Paragraph("<b>templates/courses.html</b><br/><b>templates/subjects.html</b>", code_style), Paragraph("Academic catalog managers for establishing degree programs and semester-mapped course syllabi.", td_style)],
        [Paragraph("<b>static/css/style.css</b>", code_style), Paragraph("Modern Glassmorphism stylesheet with CSS variables, responsive grid/flexbox layouts, cards, and badges.", td_style)],
        [Paragraph("<b>static/css/Js/script.js</b>", code_style), Paragraph("Client-side search script for instant row-level DOM filtering without network requests.", td_style)]
    ]
    t_fs = Table(fs_data, colWidths=[150, 337])
    t_fs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fs)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 4: DATABASE DESIGN & SCHEMA
    # =========================================================================
    story.append(Paragraph("4. Relational Database Design & Schema (डेटाबेस टेबल्स और डेटा मॉडल)", h1_style))
    story.append(Paragraph(
        "System ka database SQLite3 me structured relational schema par organized hai jisme 7 primary tables banaye gaye hain:",
        body_style
    ))

    schema_data = [
        [Paragraph("Table Name", th_style), Paragraph("Primary Columns & Types", th_style), Paragraph("Constraints & Relationships", th_style)],
        [
            Paragraph("<b>users</b>", td_bold),
            Paragraph("id (PK), username (TEXT), password_hash (TEXT), email (TEXT), full_name (TEXT), role (TEXT), created_at (TIMESTAMP)", td_style),
            Paragraph("username UNIQUE, email UNIQUE. Password hashed with PBKDF2 for admin security.", td_style)
        ],
        [
            Paragraph("<b>students</b>", td_bold),
            Paragraph("id (PK), roll_no (TEXT), name (TEXT), email (TEXT), phone (TEXT), dob (TEXT), gender (TEXT), course (TEXT), semester (INT), marks (REAL), address (TEXT), status (TEXT)", td_style),
            Paragraph("roll_no UNIQUE NOT NULL. Status defaults to 'Active'. Central entity referenced across all modules.", td_style)
        ],
        [
            Paragraph("<b>courses</b>", td_bold),
            Paragraph("id (PK), name (TEXT)", td_style),
            Paragraph("name UNIQUE NOT NULL. Represents degree programs (B.Tech, BCA, MCA, MBA).", td_style)
        ],
        [
            Paragraph("<b>subjects</b>", td_bold),
            Paragraph("id (PK), course_id (INT), semester (INT), name (TEXT)", td_style),
            Paragraph("FOREIGN KEY (course_id) REFERENCES courses(id). Maps subjects to course & semester.", td_style)
        ],
        [
            Paragraph("<b>attendance</b>", td_bold),
            Paragraph("id (PK), student_id (INT), date (TEXT), status (TEXT)", td_style),
            Paragraph("FOREIGN KEY (student_id) REFERENCES students(id). Status: 'Present', 'Absent', 'Late'.", td_style)
        ],
        [
            Paragraph("<b>marks</b>", td_bold),
            Paragraph("id (PK), student_id (INT), subject_id (INT), marks_obtained (REAL)", td_style),
            Paragraph("FOREIGN KEY (student_id) REFERENCES students(id), FOREIGN KEY (subject_id) REFERENCES subjects(id).", td_style)
        ],
        [
            Paragraph("<b>fees</b>", td_bold),
            Paragraph("id (PK), student_id (INT), total_fees (REAL), paid_fees (REAL), last_payment_date (TEXT), last_payment_amount (REAL)", td_style),
            Paragraph("student_id UNIQUE NOT NULL. FOREIGN KEY (student_id) REFERENCES students(id). Tracks dues & receipts.", td_style)
        ]
    ]

    t_schema = Table(schema_data, colWidths=[75, 235, 177])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 5: DETAILED MODULES & WHAT WAS BUILT
    # =========================================================================
    story.append(Paragraph("5. Detailed Modules & What Was Built (प्रोजेक्ट में क्या-क्या बनाया गया)", h1_style))
    story.append(Paragraph(
        "Is project me complete educational administration ke liye 8 specialized modules build kiye gaye hain:",
        body_style
    ))

    modules_info = [
        ("Module 1: Authentication & Security (Phase 4)", [
            "<b>Secure Login Portal:</b> <code>/login</code> route par username aur password authentication. Werkzeug <code>check_password_hash</code> algorithm se verify hota hai.",
            "<b>Route Guard Protection:</b> Custom <code>@login_required</code> decorator jo unauthorized users ko login page par redirect karta hai.",
            "<b>Dynamic User Badge:</b> <code>@app.context_processor</code> decorator template me globally <code>current_user</code> pass karta hai taaki sidebar me logged-in admin ka avatar aur role display ho.",
            "<b>Change Password Facility:</b> <code>/profile/change-password</code> route par admin apna password badal sakta hai jisme current password verification aur minimum 6-character validation enforced hai.",
            "<b>Default Admin Seeding:</b> Database initialization par default admin credentials (<code>admin</code> / <code>admin123</code>) automatically initialize ho jaate hain."
        ]),
        ("Module 2: Institute KPI Dashboard (Overview Center)", [
            "<b>Real-time Metrics:</b> Total Students, Active Students vs Inactive, Total Programs, Total Subjects, aur Institute Aggregate Marks.",
            "<b>Student Directory:</b> Tabular listing jisme student avatar, roll no, program, contact, score, status badge display hota hai.",
            "<b>Instant Search Filter:</b> JavaScript powered live search bar jo bina reload ke name, roll no aur course ko filter karta hai."
        ]),
        ("Module 3: Student Admission & Full CRUD Lifecycle", [
            "<b>Student Admission:</b> Roll no, Name, Email, Phone, DOB, Gender, Course, Semester, Initial Marks, Address input.",
            "<b>Strict Validations:</b> 10-digit numeric phone check, Unique Roll No check, Semester range (1-12), Marks range (0-100).",
            "<b>Student Editing & Status Toggle:</b> Details update karne aur student status ko Active/Inactive mark karne ki suvidha.",
            "<b>Secure Record Deletion:</b> POST request validation ke sath student record ko permanently delete karne ka option."
        ]),
        ("Module 4: Academic Curriculum (Courses & Subjects)", [
            "<b>Course Catalog:</b> Naye courses/degrees add ya remove karna (<code>/courses</code>).",
            "<b>Subject Mapping:</b> Subjects ko particular course aur semester ke sath link karna (<code>/subjects</code>) taaki syllabus structured rahe."
        ]),
        ("Module 5: Daily Attendance Tracking System", [
            "<b>Flexible Filtering:</b> Date selector, Course filter aur Semester filter ke sath selective student attendance list.",
            "<b>Radio Status Marking:</b> Har student ke liye Present, Absent ya Late mark karne ka simple UI.",
            "<b>Real-time Daily Stats:</b> Total marked count, Present percentage (Present + 0.5 * Late formula), Absent count calculate hota hai.",
            "<b>Smart Upsert:</b> Agar us date ka attendance pehle se hai to update hota hai, naya hone par insert hota hai."
        ]),
        ("Module 6: Marks & Examination Grading System", [
            "<b>Course & Subject Wise Scoring:</b> Particular course, semester aur subject select karke students ke marks enter kiye jaate hain.",
            "<b>Automated Average Recalculation:</b> Jaise hi kisi subject ke marks update hote hain, system student ke all-subject marks ka average calculate karke <code>students.marks</code> column me update kar deta hai."
        ]),
        ("Module 7: Fees Management & Financial Ledger", [
            "<b>Automatic Student Fee Sync:</b> Har naye student ke liye default fee (₹50,000) account automatic open hota hai.",
            "<b>Fee Customization:</b> Course fee ko student-wise customize karne ka provision.",
            "<b>Payment Collection:</b> Partial installments ya full payment record karna with payment date aur last paid receipt details.",
            "<b>Financial Overview Cards:</b> Total Expected Revenue, Total Collected, Total Outstanding Dues, Fully Paid Students Count."
        ]),
        ("Module 8: 360-Degree Comprehensive Student Profile", [
            "<b>Unified Single-Page Dossier (<code>/student/&lt;id&gt;</code>):</b> Student ki identity, personal info, roll number, course, batch.",
            "<b>Attendance Breakdown:</b> Total classes, Present count, Absent count, Late count, aur visual attendance percentage bar.",
            "<b>Academic Transcript:</b> Semester-wise subjects aur marks obtained ka complete table.",
            "<b>Financial Summary:</b> Total course fee, amount paid, balance remaining, last payment date aur receipt amount."
        ])
    ]

    for title, points in modules_info:
        story.append(Paragraph(title, h2_style))
        for p in points:
            story.append(Paragraph(f"• {p}", bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: DATA FLOW & EXECUTION LIFECYCLE
    # =========================================================================
    story.append(Paragraph("6. How the System Works & Data Flow (चीजें आपस में कैसे काम करती हैं)", h1_style))
    story.append(Paragraph(
        "Application ka flow user ke browser request se shuru hokar database persistence aur response presentation tak is tarah chalta hai:",
        body_style
    ))

    flow_data = [
        [Paragraph("Step", th_style), Paragraph("Component", th_style), Paragraph("Action & Internal Processing", th_style)],
        [
            Paragraph("<b>1</b>", td_bold),
            Paragraph("Client Request", td_style),
            Paragraph("User browser me URL enter karta hai ya HTML form submit karta hai (e.g. Admit Student form).", td_style)
        ],
        [
            Paragraph("<b>2</b>", td_bold),
            Paragraph("Security Guard", td_style),
            Paragraph("Flask routing system aur <code>@login_required</code> decorator check karte hain ki user session valid hai ya nahi.", td_style)
        ],
        [
            Paragraph("<b>3</b>", td_bold),
            Paragraph("Controller Validation", td_style),
            Paragraph("<code>app.py</code> request payload ko sanitize karta hai: blank fields, roll number duplicates, phone length, semester boundaries check karta hai.", td_style)
        ],
        [
            Paragraph("<b>4</b>", td_bold),
            Paragraph("Database Transaction", td_style),
            Paragraph("Helper function <code>get_db_connection()</code> SQLite database se connect karta hai aur parameterized queries (<code>?</code>) execute karta hai taaki SQL Injection se protection rahe.", td_style)
        ],
        [
            Paragraph("<b>5</b>", td_bold),
            Paragraph("Jinja2 Dynamic Render", td_style),
            Paragraph("Controller database rows ko fetch karke Jinja2 templates ko pass karta hai jisme <code>base.html</code> layout extend hokar complete webpage banata hai.", td_style)
        ],
        [
            Paragraph("<b>6</b>", td_bold),
            Paragraph("Client Enhancement", td_style),
            Paragraph("Browser me CSS styles load hoti hain aur <code>script.js</code> real-time table filtering provide karta hai.", td_style)
        ]
    ]

    t_flow = Table(flow_data, colWidths=[35, 115, 337])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 7: SECURITY SAFEGUARDS
    # =========================================================================
    story.append(Paragraph("7. Security & Validation Safeguards (सुरक्षा और डेटा वैलिडेशन)", h1_style))
    story.append(Paragraph(
        "System me standard security best practices incorporate kiye gaye hain taaki institutional data safe aur consistent rahe:",
        body_style
    ))
    story.append(Paragraph("• <b>Cryptographic Hashing:</b> Passwords kabhi bhi plain text me store nahi hote; Werkzeug ka PBKDF2 algorithm irreversible salt-based hash produce karta hai.", bullet_style))
    story.append(Paragraph("• <b>SQL Injection Prevention:</b> Saare database queries parameterized statements (<code>?</code> placeholders) use karte hain, jisse dynamic malicious SQL injection blocks ho jate hain.", bullet_style))
    story.append(Paragraph("• <b>Encrypted Signed Sessions:</b> User login state Flask ke cryptographically signed session cookie me secure rehti hai jo <code>app.secret_key</code> se sign hoti hai.", bullet_style))
    story.append(Paragraph("• <b>Server-Side Strict Validation:</b> Client-side HTML form ke alawa Python backend me strictly check hota hai ki Roll Number duplicate na ho, phone number 10 digits ka ho, semester 1-12 ho aur marks 0-100 ke bich hon.", bullet_style))
    story.append(Paragraph("• <b>Flash Messaging System:</b> User ko har action par feedback milta hai (e.g. green success message ya red error alert).", bullet_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 8: HOW TO SETUP & RUN
    # =========================================================================
    story.append(Paragraph("8. How to Setup & Run the Application (प्रोजेक्ट चलाने का तरीका)", h1_style))
    story.append(Paragraph(
        "Project ko run karne ke liye nimn steps follow kiye jaate hain:",
        body_style
    ))
    story.append(Paragraph("<b>Step 1: Open Terminal / Shell:</b> <code>cd \"d:\\student management project\"</code>", bullet_style))
    story.append(Paragraph("<b>Step 2: Activate Virtual Environment:</b> <code>.\\venv\\Scripts\\activate</code>", bullet_style))
    story.append(Paragraph("<b>Step 3: Run Application:</b> <code>python app.py</code> (Yeh command database tables aur default admin auto-create kar degi).", bullet_style))
    story.append(Paragraph("<b>Step 4: Access in Browser:</b> Open Chrome/Edge and navigate to <b>http://127.0.0.1:5000</b>", bullet_style))
    story.append(Paragraph("<b>Step 5: Sign In:</b> Username: <code>admin</code> | Password: <code>admin123</code>", bullet_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 9: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("9. Conclusion & Future Enhancements (निष्कर्ष और भविष्य के सुधार)", h1_style))
    story.append(Paragraph(
        "<b>Conclusion:</b> EduManage ek robust, scalable aur user-friendly Student Management System hai jo educational "
        "institutions ke operational workflow ko streamline karta hai. Iska modern Glassmorphism UI, client-side live search, "
        "aur automated calculations is project ko standard student projects se alag aur commercial-grade banate hain.",
        body_style
    ))
    story.append(Paragraph("<b>Future Scope:</b>", td_bold))
    story.append(Paragraph("• <b>Student & Parent Portal:</b> Separate student login jaha ve apna attendance record aur fee receipt download kar sakein.", bullet_style))
    story.append(Paragraph("• <b>Automated SMS / Email Alerts:</b> Absent students ke parents ko automatic SMS / Email notification.", bullet_style))
    story.append(Paragraph("• <b>Excel / CSV Bulk Export & Import:</b> Bulk student admissions aur exam score sheets ko Excel format me download karna.", bullet_style))
    story.append(Paragraph("• <b>Online Payment Gateway:</b> Razorpay / UPI integration for cashless online fee payment.", bullet_style))
    story.append(Spacer(1, 12))

    # Formal Sign-off box
    signoff_data = [
        [
            Paragraph("<b>Project Status:</b> Production Ready (Phase 4 Completed)", td_style),
            Paragraph("<b>Documentation Version:</b> 1.0.0 (Final)", td_style),
            Paragraph(f"<b>Report Compiled:</b> {datetime.now().strftime('%d-%m-%Y')}", td_style)
        ]
    ]
    t_signoff = Table(signoff_data, colWidths=[162, 162, 163])
    t_signoff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), card_bg),
        ('BOX', (0,0), (-1,-1), 1, primary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_signoff)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: Comprehensive PDF generated successfully at: {filename}")

if __name__ == "__main__":
    generate_pdf()
