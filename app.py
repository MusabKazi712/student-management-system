from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import date, datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key" # Required for flash messages

DATABASE = "database.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            semester INTEGER NOT NULL,
            marks REAL NOT NULL,
            address TEXT NOT NULL,
            status TEXT DEFAULT 'Active'
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks_obtained REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            total_fees REAL NOT NULL DEFAULT 0,
            paid_fees REAL NOT NULL DEFAULT 0,
            last_payment_date TEXT,
            last_payment_amount REAL DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        """
    )

    # Users / Admins table for Phase 4 Authentication
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Seed default admin user if not exists
    admin_user = connection.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if not admin_user:
        connection.execute(
            """
            INSERT INTO users (username, password_hash, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", generate_password_hash("admin123"), "admin@edumanage.com", "Administrator", "Admin")
        )

    # Add status column to existing students if it doesn't exist
    try:
        connection.execute("ALTER TABLE students ADD COLUMN status TEXT DEFAULT 'Active'")
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


# --- Authentication & Session Security (Phase 4) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access the system.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_user():
    return {
        "current_user": {
            "id": session.get("user_id"),
            "username": session.get("username"),
            "full_name": session.get("full_name"),
            "role": session.get("role")
        } if "user_id" in session else None
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        connection = get_db_connection()
        user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")

            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required.", "error")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New password and confirmation password do not match.", "error")
            return redirect(url_for("change_password"))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "error")
            return redirect(url_for("change_password"))

        connection = get_db_connection()
        user = connection.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        if not user or not check_password_hash(user["password_hash"], current_password):
            connection.close()
            flash("Current password is incorrect.", "error")
            return redirect(url_for("change_password"))

        connection.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), session["user_id"])
        )
        connection.commit()
        connection.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for("home"))

    return render_template("change_password.html")


@app.route("/")
@login_required
def home():
    connection = get_db_connection()

    # All students
    students = connection.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    # Count total students
    total_students = connection.execute(
        "SELECT COUNT(*) AS count FROM students"
    ).fetchone()["count"]

    # Count active students
    active_students = connection.execute(
        "SELECT COUNT(*) AS count FROM students WHERE status = 'Active'"
    ).fetchone()["count"]

    # Count unique/active courses
    active_courses = connection.execute(
        "SELECT COUNT(DISTINCT course) AS count FROM students"
    ).fetchone()["count"]

    # Count total subjects
    total_subjects = connection.execute(
        "SELECT COUNT(*) AS count FROM subjects"
    ).fetchone()["count"]

    # Average marks
    avg_marks = connection.execute(
        "SELECT AVG(marks) AS avg_marks FROM students"
    ).fetchone()["avg_marks"]
    avg_marks = round(avg_marks, 2) if avg_marks else 0

    connection.close()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        active_students=active_students,
        active_courses=active_courses,
        total_subjects=total_subjects,
        avg_marks=avg_marks
    )

@app.route("/student/<int:id>")
@login_required
def profile(id):
    connection = get_db_connection()
    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()
    
    if student is None:
        connection.close()
        flash("Student not found", "error")
        return redirect(url_for("home"))

    # Attendance stats
    total_attendance = connection.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE student_id = ?", (id,)
    ).fetchone()["count"]
    present_attendance = connection.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE student_id = ? AND status = 'Present'", (id,)
    ).fetchone()["count"]
    late_attendance = connection.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE student_id = ? AND status = 'Late'", (id,)
    ).fetchone()["count"]
    absent_attendance = connection.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE student_id = ? AND status = 'Absent'", (id,)
    ).fetchone()["count"]
    
    att_percent = round((present_attendance + 0.5 * late_attendance) / total_attendance * 100, 1) if total_attendance > 0 else 0

    # Subject-wise marks
    subject_marks = connection.execute(
        """
        SELECT marks.marks_obtained, subjects.name as subject_name, subjects.semester
        FROM marks
        JOIN subjects ON marks.subject_id = subjects.id
        WHERE marks.student_id = ?
        ORDER BY subjects.semester, subjects.name
        """,
        (id,)
    ).fetchall()

    # Fee status
    fee_record = connection.execute(
        "SELECT * FROM fees WHERE student_id = ?", (id,)
    ).fetchone()
    
    if not fee_record:
        connection.execute(
            "INSERT INTO fees (student_id, total_fees, paid_fees) VALUES (?, 50000, 0)",
            (id,)
        )
        connection.commit()
        fee_record = connection.execute("SELECT * FROM fees WHERE student_id = ?", (id,)).fetchone()

    connection.close()
    return render_template(
        "profile.html",
        student=student,
        total_attendance=total_attendance,
        present_attendance=present_attendance,
        late_attendance=late_attendance,
        absent_attendance=absent_attendance,
        att_percent=att_percent,
        subject_marks=subject_marks,
        fee_record=fee_record
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        # Form data
        roll_no = request.form["roll_no"].strip()
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        dob = request.form["dob"].strip()
        gender = request.form["gender"].strip()
        course = request.form["course"].strip()
        address = request.form["address"].strip()

        try:
            semester = int(request.form["semester"])
            marks = float(request.form["marks"])
        except ValueError:
            flash("Invalid semester or marks", "error")
            return redirect(url_for("add_student"))

        # Validation
        if not (roll_no and name and email and phone and dob and gender and course and address):
            flash("All fields are required", "error")
            return redirect(url_for("add_student"))

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must be exactly 10 digits", "error")
            return redirect(url_for("add_student"))

        if semester < 1 or semester > 12:
            flash("Semester must be between 1 and 12", "error")
            return redirect(url_for("add_student"))

        if marks < 0 or marks > 100:
            flash("Marks must be between 0 and 100", "error")
            return redirect(url_for("add_student"))

        # Save student
        connection = get_db_connection()
        
        # Check if roll no exists
        existing = connection.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,)).fetchone()
        if existing:
            flash("Roll Number already exists!", "error")
            connection.close()
            return redirect(url_for("add_student"))

        try:
            connection.execute(
                """
                INSERT INTO students
                (roll_no, name, email, phone, dob, gender, course, semester, marks, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (roll_no, name, email, phone, dob, gender, course, semester, marks, address)
            )
            connection.commit()
            flash("Student added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Error saving student data.", "error")
        finally:
            connection.close()

        return redirect(url_for("home"))

    connection = get_db_connection()
    courses = connection.execute("SELECT * FROM courses ORDER BY name").fetchall()
    connection.close()
    return render_template("add_student.html", courses=courses)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    connection = get_db_connection()
    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if student is None:
        connection.close()
        flash("Student not found", "error")
        return redirect(url_for("home"))

    if request.method == "POST":

        roll_no = request.form["roll_no"].strip()
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        dob = request.form["dob"].strip()
        gender = request.form["gender"].strip()
        course = request.form["course"].strip()
        address = request.form["address"].strip()
        status = request.form.get("status", "Active").strip()

        try:
            semester = int(request.form["semester"])
            marks = float(request.form["marks"])
        except ValueError:
            connection.close()
            flash("Invalid semester or marks", "error")
            return redirect(url_for("edit_student", id=id))

        if not (roll_no and name and email and phone and dob and gender and course and address):
            connection.close()
            flash("All fields are required", "error")
            return redirect(url_for("edit_student", id=id))

        if not phone.isdigit() or len(phone) != 10:
            connection.close()
            flash("Phone number must be exactly 10 digits", "error")
            return redirect(url_for("edit_student", id=id))

        if semester < 1 or semester > 12:
            connection.close()
            flash("Semester must be between 1 and 12", "error")
            return redirect(url_for("edit_student", id=id))

        if marks < 0 or marks > 100:
            connection.close()
            flash("Marks must be between 0 and 100", "error")
            return redirect(url_for("edit_student", id=id))

        # Check if new roll no conflicts with other users
        existing = connection.execute("SELECT id FROM students WHERE roll_no = ? AND id != ?", (roll_no, id)).fetchone()
        if existing:
            connection.close()
            flash("Roll Number already exists for another student!", "error")
            return redirect(url_for("edit_student", id=id))

        try:
            connection.execute(
                """
                UPDATE students
                SET roll_no = ?, name = ?, email = ?, phone = ?, dob = ?, gender = ?, course = ?, semester = ?, marks = ?, address = ?, status = ?
                WHERE id = ?
                """,
                (roll_no, name, email, phone, dob, gender, course, semester, marks, address, status, id)
            )
            connection.commit()
            flash("Student updated successfully!", "success")
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "error")
        finally:
            connection.close()

        return redirect(url_for("home"))

    courses = connection.execute("SELECT * FROM courses ORDER BY name").fetchall()
    connection.close()

    return render_template(
        "edit_student.html",
        student=student,
        courses=courses
    )


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):

    connection = get_db_connection()
    connection.execute("DELETE FROM students WHERE id = ?", (id,))
    connection.commit()
    connection.close()

    flash("Student record deleted successfully!", "success")
    return redirect(url_for("home"))


# --- Course Routes ---
@app.route("/courses")
@login_required
def courses():
    connection = get_db_connection()
    courses = connection.execute("SELECT * FROM courses ORDER BY id DESC").fetchall()
    connection.close()
    return render_template("courses.html", courses=courses)

@app.route("/courses/add", methods=["POST"])
@login_required
def add_course():
    name = request.form["name"].strip()
    if not name:
        flash("Course name is required", "error")
        return redirect(url_for("courses"))
        
    connection = get_db_connection()
    try:
        connection.execute("INSERT INTO courses (name) VALUES (?)", (name,))
        connection.commit()
        flash("Course added successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Course already exists!", "error")
    finally:
        connection.close()
    return redirect(url_for("courses"))

@app.route("/courses/delete/<int:id>", methods=["POST"])
@login_required
def delete_course(id):
    connection = get_db_connection()
    connection.execute("DELETE FROM courses WHERE id = ?", (id,))
    connection.commit()
    connection.close()
    flash("Course deleted successfully!", "success")
    return redirect(url_for("courses"))


# --- Subject Routes ---
@app.route("/subjects")
@login_required
def subjects():
    connection = get_db_connection()
    subjects = connection.execute(
        """
        SELECT subjects.*, courses.name as course_name 
        FROM subjects 
        JOIN courses ON subjects.course_id = courses.id 
        ORDER BY subjects.id DESC
        """
    ).fetchall()
    courses = connection.execute("SELECT * FROM courses ORDER BY name").fetchall()
    connection.close()
    return render_template("subjects.html", subjects=subjects, courses=courses)

@app.route("/subjects/add", methods=["POST"])
@login_required
def add_subject():
    name = request.form["name"].strip()
    try:
        course_id = int(request.form["course_id"])
        semester = int(request.form["semester"])
    except ValueError:
        flash("Invalid course or semester", "error")
        return redirect(url_for("subjects"))
        
    if not name:
        flash("Subject name is required", "error")
        return redirect(url_for("subjects"))
        
    connection = get_db_connection()
    connection.execute("INSERT INTO subjects (course_id, semester, name) VALUES (?, ?, ?)", (course_id, semester, name))
    connection.commit()
    connection.close()
    flash("Subject added successfully!", "success")
    return redirect(url_for("subjects"))

@app.route("/subjects/delete/<int:id>", methods=["POST"])
@login_required
def delete_subject(id):
    connection = get_db_connection()
    connection.execute("DELETE FROM subjects WHERE id = ?", (id,))
    connection.commit()
    connection.close()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("subjects"))


# --- Attendance Routes (Phase 3) ---
@app.route("/attendance", methods=["GET"])
@login_required
def attendance():
    today_str = date.today().isoformat()
    selected_date = request.args.get("date", today_str).strip() or today_str
    selected_course = request.args.get("course", "").strip()
    selected_semester = request.args.get("semester", "").strip()

    connection = get_db_connection()
    courses = connection.execute("SELECT * FROM courses ORDER BY name").fetchall()

    query = "SELECT * FROM students WHERE status = 'Active'"
    params = []

    if selected_course:
        query += " AND course = ?"
        params.append(selected_course)

    if selected_semester:
        try:
            sem_int = int(selected_semester)
            query += " AND semester = ?"
            params.append(sem_int)
        except ValueError:
            pass

    query += " ORDER BY roll_no ASC"
    students = connection.execute(query, params).fetchall()

    # Existing attendance for selected_date
    existing_records = connection.execute(
        "SELECT student_id, status FROM attendance WHERE date = ?",
        (selected_date,)
    ).fetchall()
    attendance_map = {row["student_id"]: row["status"] for row in existing_records}

    # Daily Stats for this date
    all_date_records = connection.execute(
        "SELECT status, COUNT(*) as cnt FROM attendance WHERE date = ? GROUP BY status",
        (selected_date,)
    ).fetchall()
    stats = {"Present": 0, "Absent": 0, "Late": 0}
    for r in all_date_records:
        if r["status"] in stats:
            stats[r["status"]] = r["cnt"]

    total_marked = sum(stats.values())
    present_pct = round((stats["Present"] + 0.5 * stats["Late"]) / total_marked * 100, 1) if total_marked > 0 else 0

    connection.close()

    return render_template(
        "attendance.html",
        courses=courses,
        students=students,
        selected_date=selected_date,
        selected_course=selected_course,
        selected_semester=selected_semester,
        attendance_map=attendance_map,
        stats=stats,
        total_marked=total_marked,
        present_pct=present_pct
    )


@app.route("/attendance/save", methods=["POST"])
@login_required
def save_attendance():
    att_date = request.form.get("date", "").strip()
    if not att_date:
        att_date = date.today().isoformat()

    selected_course = request.form.get("course", "").strip()
    selected_semester = request.form.get("semester", "").strip()

    connection = get_db_connection()

    for key, value in request.form.items():
        if key.startswith("status_"):
            try:
                student_id = int(key.replace("status_", ""))
                status = value.strip()
                if status in ["Present", "Absent", "Late"]:
                    existing = connection.execute(
                        "SELECT id FROM attendance WHERE student_id = ? AND date = ?",
                        (student_id, att_date)
                    ).fetchone()
                    if existing:
                        connection.execute(
                            "UPDATE attendance SET status = ? WHERE id = ?",
                            (status, existing["id"])
                        )
                    else:
                        connection.execute(
                            "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                            (student_id, att_date, status)
                        )
            except ValueError:
                continue

    connection.commit()
    connection.close()

    flash(f"Attendance recorded successfully for {att_date}!", "success")
    return redirect(url_for("attendance", date=att_date, course=selected_course, semester=selected_semester))


# --- Marks & Examination Routes (Phase 3) ---
@app.route("/marks", methods=["GET"])
@login_required
def marks():
    connection = get_db_connection()
    courses = connection.execute("SELECT * FROM courses ORDER BY name").fetchall()
    all_subjects = connection.execute(
        """
        SELECT subjects.*, courses.name as course_name 
        FROM subjects 
        JOIN courses ON subjects.course_id = courses.id 
        ORDER BY subjects.name
        """
    ).fetchall()

    course_id = request.args.get("course_id", type=int)
    semester = request.args.get("semester", type=int)
    subject_id = request.args.get("subject_id", type=int)

    selected_course = None
    if course_id:
        selected_course = connection.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()

    selected_subject = None
    if subject_id:
        selected_subject = connection.execute(
            """
            SELECT subjects.*, courses.name as course_name 
            FROM subjects 
            JOIN courses ON subjects.course_id = courses.id 
            WHERE subjects.id = ?
            """,
            (subject_id,)
        ).fetchone()

    students = []
    marks_map = {}
    if selected_course and semester and selected_subject:
        students = connection.execute(
            "SELECT * FROM students WHERE course = ? AND semester = ? AND status = 'Active' ORDER BY roll_no ASC",
            (selected_course["name"], semester)
        ).fetchall()

        marks_records = connection.execute(
            "SELECT student_id, marks_obtained FROM marks WHERE subject_id = ?",
            (selected_subject["id"],)
        ).fetchall()
        marks_map = {r["student_id"]: r["marks_obtained"] for r in marks_records}

    connection.close()

    return render_template(
        "marks.html",
        courses=courses,
        all_subjects=all_subjects,
        selected_course_id=course_id,
        selected_semester=semester,
        selected_subject_id=subject_id,
        selected_subject=selected_subject,
        students=students,
        marks_map=marks_map
    )


@app.route("/marks/save", methods=["POST"])
@login_required
def save_marks():
    try:
        subject_id = int(request.form["subject_id"])
        course_id = request.form.get("course_id", "")
        semester = request.form.get("semester", "")
    except (KeyError, ValueError):
        flash("Invalid subject or course selection.", "error")
        return redirect(url_for("marks"))

    connection = get_db_connection()

    for key, value in request.form.items():
        if key.startswith("marks_"):
            try:
                student_id = int(key.replace("marks_", ""))
                score_str = value.strip()
                if score_str == "":
                    continue
                score = float(score_str)
                if score < 0 or score > 100:
                    continue

                existing = connection.execute(
                    "SELECT id FROM marks WHERE student_id = ? AND subject_id = ?",
                    (student_id, subject_id)
                ).fetchone()

                if existing:
                    connection.execute(
                        "UPDATE marks SET marks_obtained = ? WHERE id = ?",
                        (score, existing["id"])
                    )
                else:
                    connection.execute(
                        "INSERT INTO marks (student_id, subject_id, marks_obtained) VALUES (?, ?, ?)",
                        (student_id, subject_id, score)
                    )

                # Recalculate student overall average across subjects
                avg_row = connection.execute(
                    "SELECT AVG(marks_obtained) as avg_score FROM marks WHERE student_id = ?",
                    (student_id,)
                ).fetchone()
                if avg_row and avg_row["avg_score"] is not None:
                    connection.execute(
                        "UPDATE students SET marks = ? WHERE id = ?",
                        (round(avg_row["avg_score"], 2), student_id)
                    )
            except ValueError:
                continue

    connection.commit()
    connection.close()

    flash("Examination marks recorded and student overall score updated!", "success")
    return redirect(url_for("marks", course_id=course_id, semester=semester, subject_id=subject_id))


# --- Fees Management Routes (Phase 3) ---
@app.route("/fees", methods=["GET"])
@login_required
def fees():
    connection = get_db_connection()

    # Sync missing students into fees table with default fee (50000)
    students = connection.execute("SELECT id FROM students").fetchall()
    for s in students:
        exists = connection.execute("SELECT id FROM fees WHERE student_id = ?", (s["id"],)).fetchone()
        if not exists:
            connection.execute(
                "INSERT INTO fees (student_id, total_fees, paid_fees) VALUES (?, 50000, 0)",
                (s["id"],)
            )
    connection.commit()

    fee_list = connection.execute(
        """
        SELECT 
            students.id as student_id,
            students.roll_no,
            students.name,
            students.course,
            students.semester,
            fees.total_fees,
            fees.paid_fees,
            (fees.total_fees - fees.paid_fees) as pending_fees,
            fees.last_payment_date,
            fees.last_payment_amount
        FROM students
        JOIN fees ON students.id = fees.student_id
        ORDER BY students.id DESC
        """
    ).fetchall()

    # Stats
    total_expected = connection.execute("SELECT SUM(total_fees) as total FROM fees").fetchone()["total"] or 0
    total_collected = connection.execute("SELECT SUM(paid_fees) as total FROM fees").fetchone()["total"] or 0
    total_due = max(0, total_expected - total_collected)
    fully_paid_count = connection.execute("SELECT COUNT(*) as cnt FROM fees WHERE paid_fees >= total_fees AND total_fees > 0").fetchone()["cnt"] or 0

    connection.close()

    return render_template(
        "fees.html",
        fee_list=fee_list,
        total_expected=total_expected,
        total_collected=total_collected,
        total_due=total_due,
        fully_paid_count=fully_paid_count
    )


@app.route("/fees/pay/<int:student_id>", methods=["POST"])
@login_required
def record_fee_payment(student_id):
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        flash("Invalid payment amount.", "error")
        return redirect(url_for("fees"))

    if amount <= 0:
        flash("Payment amount must be greater than 0.", "error")
        return redirect(url_for("fees"))

    pay_date = request.form.get("payment_date", "").strip() or date.today().isoformat()

    connection = get_db_connection()
    fee_row = connection.execute("SELECT * FROM fees WHERE student_id = ?", (student_id,)).fetchone()

    if not fee_row:
        connection.execute(
            "INSERT INTO fees (student_id, total_fees, paid_fees, last_payment_date, last_payment_amount) VALUES (?, 50000, ?, ?, ?)",
            (student_id, amount, pay_date, amount)
        )
    else:
        new_paid = fee_row["paid_fees"] + amount
        connection.execute(
            """
            UPDATE fees 
            SET paid_fees = ?, last_payment_date = ?, last_payment_amount = ? 
            WHERE student_id = ?
            """,
            (new_paid, pay_date, amount, student_id)
        )

    connection.commit()
    connection.close()

    flash(f"Payment of ₹{amount:,.2f} recorded successfully!", "success")
    return redirect(url_for("fees"))


@app.route("/fees/update-total/<int:student_id>", methods=["POST"])
@login_required
def update_total_fee(student_id):
    try:
        total_fees = float(request.form.get("total_fees", 0))
    except ValueError:
        flash("Invalid total fee amount.", "error")
        return redirect(url_for("fees"))

    if total_fees < 0:
        flash("Total fee cannot be negative.", "error")
        return redirect(url_for("fees"))

    connection = get_db_connection()
    connection.execute("UPDATE fees SET total_fees = ? WHERE student_id = ?", (total_fees, student_id))
    connection.commit()
    connection.close()

    flash("Total course fee updated successfully!", "success")
    return redirect(url_for("fees"))


if __name__ == "__main__":
    create_database()
    app.run(debug=True)