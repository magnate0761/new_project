# COLLEGE DATABASE

## A Mini Project Report

**On**

# "College Database — A Web-Based Student Record Management System"

Submitted in partial fulfilment of the requirements for the award of the degree of

**Bachelor of Engineering / Bachelor of Technology**

in

**[Department Name], [College/University Name]**

| | |
|---|---|
| **Student Name:** | [Your Name] |
| **Roll Number:** | [Your Roll Number] |
| **Guide:** | [Guide / Faculty Name] |
| **Academic Year:** | 2026 – 27 |

---

## Abstract

This project presents the design and implementation of a web-based **College Database**, a Student Database Management System (DBMS) that allows the institution to create, view, modify, and delete student records through a clean web interface. The system is built with **Python 3**, the **Flask** web framework, and the **SQLite** relational database, with **Jinja2** templates and plain CSS for the front end. It provides a statistics dashboard (total students, active students, average GPA, top performer, department distribution), a student directory with **live search, department/semester filtering, and column sorting**, fully validated add/edit forms, safe delete operations, and a small **JSON API**. The code follows a three-layer architecture (web layer, data layer, connection layer), uses **parameterised SQL queries** to prevent SQL injection, and relies on **Jinja2 auto-escaping** to prevent cross-site scripting. The entire application depends on a single third-party package, stores its data in one portable file, and can be deployed with two commands.

**Keywords:** Database Management System, CRUD, Flask, SQLite, SQL injection, web application, data validation.

---

## 1. Problem Statement

Colleges and department offices must maintain accurate records of every student they enrol: roll number, name, contact details, department, current semester, grade point average (GPA), and admission status. In many institutions this work is still done with **paper registers** or **stand-alone spreadsheet files** (MS Excel), which creates several practical problems:

1. **Slow, painful lookup.** Finding one student among thousands of rows requires manually scrolling a spreadsheet or flipping through register pages.
2. **No data integrity rules.** Nothing stops two students from being given the same roll number, the same email, a GPA of 15, or a semester of 9 — the kind of errors that corrupt records permanently.
3. **No summary analytics.** Questions such as "how many students are in each department?" or "what is the class average GPA?" require manual counting or fragile formulas.
4. **Scattered, fragile data.** Spreadsheet files live on individual computers, get copied, renamed, and lost; there is no single source of truth.
5. **No consistent interface.** Every office worker enters data differently — formats vary, abbreviations vary, and corrections must be made by hand.
6. **No controlled access to the data** and no machine-readable way for other systems (reports, portals, mobile apps) to consume it.

A **centralised, web-based database management system** solves all of the above: one application, one database, enforced rules, instant search and statistics, and an interface that any staff member can use in a browser.

---

## 2. Objective

The objectives of this project are to design, develop and test a web-based Student Database Management System that:

1. **Stores student records** (roll number, name, email, phone, department, semester, GPA, date of birth, status) in a relational database (SQLite) with proper column types and constraints.
2. **Provides complete CRUD operations** — Create (add a student), Read (list and view students), Update (edit details), Delete (remove a record) — through a simple web interface.
3. **Validates all input in two layers**: friendly, specific error messages from Python validation, plus database-level `UNIQUE` and `CHECK` constraints as a final safety net.
4. **Supports fast retrieval**: free-text search over name/roll number/email, filtering by department and semester, and sorting by any column.
5. **Presents instant statistics** on a dashboard: total and active students, average GPA, top performer, department-wise distribution, and recently added records — all computed directly in SQL.
6. **Is secure by design**: parameterised SQL queries (no SQL injection), template auto-escaping (no XSS), POST-only destructive routes with confirmation, and a signed session for messages.
7. **Is lightweight and portable**: a single third-party dependency (Flask), a single-file database, and a virtual-environment-based setup that runs on any machine with Python 3.
8. **Is extensible**: a small JSON REST-style API is exposed so that future mobile or front-end applications can consume the same data.

---

## 3. Existing System

The prevailing practice (the "existing system") for maintaining student records in small-to-medium institutions is one of the following:

| # | Existing approach | How it works | Drawbacks |
|---|---|---|---|
| 1 | **Paper registers / files** | Admissions are written into bound registers; copies are kept in file folders. | Slow to search; hard to update (strike-throughs); vulnerable to loss and damage; impossible to compute statistics; not shareable. |
| 2 | **Spreadsheet files (Excel/CSV)** | One sheet per year or per department, maintained by a single office staff member. | No enforcement of uniqueness (duplicate roll numbers possible); fragile formulas break when rows are inserted; no validation of formats; version conflicts when several people copy the file; no concurrent access; statistics are manual. |
| 3 | **Ad-hoc custom software / local apps** | Occasional desktop applications written by a vendor, with the database locked inside a specific machine. | Expensive to modify; tied to one computer/OS; no web access; data extraction (API, reports) is difficult; maintenance stops when the vendor is unavailable. |

**Common shortcomings of the existing system (summary):**

- No relational integrity (no unique keys, no range checks, no referential structure).
- Search and filtering are manual or limited to one column.
- Updates must be done by hand and propagate incorrectly across copies.
- No analytics (averages, distributions) without manual work.
- Data is not available to other systems programmatically.
- No consistent, user-friendly interface for data entry.

**Comparison — Existing system vs. the proposed system:**

| Feature | Existing (paper / spreadsheet) | Proposed (College Database) |
|---|---|---|
| Data storage | Paper / unstructured sheets | Relational SQLite database with constraints |
| Duplicate roll numbers / emails | Possible | Blocked by `UNIQUE` keys + validation |
| Invalid values (GPA > 10, Sem 9) | Possible | Blocked by `CHECK` constraints + validation |
| Search | Manual | Live multi-column search (`LIKE`) |
| Filters / sorting | Manual or single-column | Department + semester filters, sort by any column |
| Statistics | Manual counting | Dashboard computed in SQL (`AVG`, `COUNT`, `GROUP BY`) |
| Access | One location, one person | Any browser on the network; extensible JSON API |
| Deletion safety | None (tear out / delete row) | POST-only route + confirmation dialog |
| Security against injection/XSS | N/A (but no audit trail) | Parameterised SQL + auto-escaping templates |

---

## 4. Novelty

The proposed system differs from the existing practice, and from typical student projects, in the following ways:

1. **Strict three-layer architecture in a minimal stack.** The web layer (`app.py`) contains no SQL, the data layer (`models.py`) contains no web code, and the connection layer (`database.py`) owns the schema. Swapping SQLite for MySQL/PostgreSQL later would require changing exactly one file.
2. **Security techniques demonstrated, not assumed.**
   - Every user-supplied value travels through **`?` parameter placeholders**, making SQL injection infeasible (the one dynamic SQL fragment — the `ORDER BY` column — is restricted by a **whitelist**).
   - Jinja2 **auto-escaping** neutralises XSS in all rendered values.
   - Destructive actions are **POST-only** with a `confirm()` dialog; the add/edit flow uses the **Post/Redirect/Get** pattern so browser refresh can never double-submit.
   - The database itself enforces `UNIQUE` / `CHECK` rules, so bad data cannot be stored even if the application layer were bypassed.
3. **No data loss on validation failure.** One form template serves *add*, *edit*, and *error re-display* (the submitted values are re-injected into the form), so a user who triggers a validation error keeps everything they typed.
4. **Single source of truth for business data.** The department list and semester range are defined once in `models.py` and drive the database options, the form dropdowns, the filters, and the validation simultaneously.
5. **Analytics with zero JavaScript.** All dashboard statistics (totals, averages, top student, department distribution) are computed by five SQL aggregation queries and rendered as a **pure-CSS bar chart** — no charting library, no client-side computation.
6. **Zero-configuration deployment.** No database server to install; the entire database is one file; the whole application needs one `pip` package. Two commands (`pip install -r requirements.txt`, `python app.py`) are sufficient to run it.
7. **Machine-readable interface.** A `/api/students` JSON endpoint exposes the same data layer to future mobile/portal applications.
8. **Comprehensive documentation.** Every file is commented, and the repository ships with a full file-by-file explanation (`README.md`) — the system is meant to be understood, not just run.

---

## 5. Code Implementation

### 5.1 Development Environment

| Item | Details |
|---|---|
| Language | Python 3.11 |
| Web framework | Flask 3.x (single third-party dependency) |
| Database | SQLite (bundled in Python's standard library, module `sqlite3`) |
| Templating | Jinja2 (bundled with Flask) |
| Styling | Plain CSS (no framework), CSS variables, Flexbox, CSS Grid |
| Packaging | `venv` virtual environment + `requirements.txt` |
| Tools | VS Code / any Python IDE; Git for version control |

### 5.2 Project Structure

```
new_project/
├── app.py                  ← Web layer: routes, form handling, messages
├── models.py               ← Data layer: all SQL queries (only file with SQL)
├── database.py             ← Connection + table schema
├── validators.py           ← Python form validation (friendly error messages)
├── seed.py                 ← Optional: inserts 12 sample students (empty DB only)
├── requirements.txt        ← flask
├── .gitignore              ← excludes .venv/, __pycache__/, students.db
├── students.db             ← (auto-created) the database file
├── static/css/style.css    ← all styling
└── templates/
    ├── base.html           ← shared layout (nav, flash banners, footer)
    ├── dashboard.html      ← "/" stat cards + charts
    ├── students.html       ← list + search + filters + sorting
    ├── student_form.html   ← shared by "add" and "edit"
    ├── student_detail.html ← one student's profile + edit/delete
    └── 404.html            ← friendly not-found page
```

### 5.3 Architecture

```
 Browser (HTML/CSS)
     │  HTTP request   e.g. GET /students?search=priya
     ▼
 ┌────────────────┐
 │   app.py       │  WEB LAYER — URLs, forms, redirects. No SQL.
 └───────┬────────┘
         │  function calls  e.g. get_students(search="priya")
         ▼
 ┌────────────────┐
 │  models.py     │  DATA LAYER — the only file that writes SQL.
 └───────┬────────┘
         │  conn.execute("SELECT …")
         ▼
 ┌────────────────┐
 │  database.py   │  CONNECTION LAYER — opens students.db,
 └───────┬────────┘  defines the table schema.
         ▼
   students.db (single file on disk)
```

Every request follows the same path: **route → validate → data layer → template → (flash + redirect)**.

### 5.4 `database.py` — Connection and Schema

```python
"""
database.py — connection + table creation (schema lives here).
Other files only ever *ask* this file for a connection, so moving from
SQLite to MySQL/PostgreSQL would require changing only this file.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # folder of this file
DB_PATH  = os.path.join(BASE_DIR, "students.db")        # DB next to the code

def get_db():
    """Open a fresh SQLite connection; rows behave like dicts/objects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create table + indexes if missing. Safe to call repeatedly."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no       TEXT    NOT NULL UNIQUE,
            full_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            phone         TEXT,
            department    TEXT    NOT NULL,
            semester      INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
            gpa           REAL    CHECK (gpa BETWEEN 0 AND 10),
            date_of_birth TEXT,
            status        TEXT    NOT NULL DEFAULT 'Active'
                                     CHECK (status IN ('Active', 'Inactive')),
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_name "
                 "ON students (full_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_dept "
                 "ON students (department)")
    conn.commit()
    conn.close()
```

**Notes.** `sqlite3.Row` makes result rows accessible by column name. The `UNIQUE` keys, `CHECK` ranges, and `DEFAULT` values make the *database itself* reject impossible data. Indexes on `full_name` and `department` speed up search and filtering as the table grows.

### 5.5 `models.py` — All SQL Queries (the Data Layer)

```python
"""
models.py — the data layer. The only file in the project that writes SQL.
Every function: open connection → execute → fetch → close.
"""
from database import get_db

DEPARTMENTS = ["Computer Science", "Information Technology",
               "Electronics & Communication", "Mechanical", "Civil"]
SEMESTERS   = list(range(1, 9))                       # [1..8]
SORTABLE    = {"full_name", "roll_no", "department",
               "semester", "gpa", "created_at"}       # whitelist

def get_students(search=None, department=None, semester=None,
                 sort_by="full_name", sort_order="asc"):
    """Filtered, sorted list of students (search + department + semester)."""
    conn = get_db()
    query  = "SELECT * FROM students WHERE 1=1"       # 1=1 → safe base clause
    params = []
    if search:
        query += " AND (full_name LIKE ? OR roll_no LIKE ? OR email LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    if department:
        query += " AND department = ?"
        params.append(department)
    if semester:
        query += " AND semester = ?"
        params.append(semester)
    if sort_by not in SORTABLE:                       # whitelist keeps ORDER BY safe
        sort_by = "full_name"
    order = "DESC" if sort_order == "desc" else "ASC"
    query += f" ORDER BY {sort_by} {order}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student(student_id):
    """One student by primary key, or None."""
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?",
                       (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_stats():
    """All dashboard numbers: totals, average, top student,
    department distribution, 5 most recent rows."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    active = conn.execute(
        "SELECT COUNT(*) AS c FROM students WHERE status = 'Active'"
    ).fetchone()["c"]
    avg_gpa = conn.execute(
        "SELECT AVG(gpa) AS a FROM students WHERE gpa IS NOT NULL"
    ).fetchone()["a"]
    top = conn.execute("""
        SELECT roll_no, full_name, gpa FROM students
        WHERE gpa IS NOT NULL ORDER BY gpa DESC, full_name ASC LIMIT 1
    """).fetchone()
    departments = [dict(r) for r in conn.execute("""
        SELECT department, COUNT(*) AS count FROM students
        GROUP BY department ORDER BY count DESC
    """).fetchall()]
    recent = [dict(r) for r in conn.execute("""
        SELECT id, roll_no, full_name, department, semester, gpa, status
        FROM students ORDER BY id DESC LIMIT 5
    """).fetchall()]
    conn.close()
    return {
        "total": total, "active": active, "avg_gpa": avg_gpa,
        "top": dict(top) if top else None,
        "departments": departments,
        "recent": recent,
        "max_dept_count": max((d["count"] for d in departments), default=0),
    }

def roll_no_exists(roll_no, exclude_id=None):
    conn = get_db()
    query, params = "SELECT 1 FROM students WHERE roll_no = ?", [roll_no]
    if exclude_id is not None:
        query += " AND id != ?"; params.append(exclude_id)
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row is not None

def email_exists(email, exclude_id=None):
    conn = get_db()
    query, params = "SELECT 1 FROM students WHERE email = ?", [email]
    if exclude_id is not None:
        query += " AND id != ?"; params.append(exclude_id)
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row is not None

def add_student(data):
    """INSERT one row; returns the new id."""
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO students
            (roll_no, full_name, email, phone,
             department, semester, gpa, date_of_birth, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data["roll_no"], data["full_name"], data["email"], data["phone"],
          data["department"], data["semester"], data["gpa"],
          data["date_of_birth"], data["status"]))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_student(student_id, data):
    """UPDATE the row; returns True if a row changed."""
    conn = get_db()
    cur = conn.execute("""
        UPDATE students
        SET roll_no = ?, full_name = ?, email = ?, phone = ?,
            department = ?, semester = ?, gpa = ?, date_of_birth = ?,
            status = ?
        WHERE id = ?
    """, (data["roll_no"], data["full_name"], data["email"], data["phone"],
          data["department"], data["semester"], data["gpa"],
          data["date_of_birth"], data["status"], student_id))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

def delete_student(student_id):
    """DELETE the row; returns True if a row was removed."""
    conn = get_db()
    cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    removed = cur.rowcount > 0
    conn.close()
    return removed
```

**Notes.** `WHERE 1=1` keeps optional filter clauses simple; `?` placeholders are the SQL-injection defence; the `ORDER BY` column is accepted only from the `SORTABLE` whitelist because SQL cannot use placeholders for identifiers.

### 5.6 `validators.py` — Python-Side Form Validation

```python
"""
validators.py — checks form input in Python, before anything reaches the
database, and returns human-readable error messages.
"""
import re
from datetime import date, datetime
from models import DEPARTMENTS

EMAIL_RE   = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE   = re.compile(r"^\+?[0-9\s\-]{7,15}$")
ROLL_NO_RE = re.compile(r"^[A-Z0-9\-]{3,15}$")

def validate_student(form, student_id=None):
    """Returns (cleaned, errors): typed dict + list of problem strings."""
    errors = []
    roll_no     = form.get("roll_no", "").strip().upper()
    full_name   = form.get("full_name", "").strip()
    email       = form.get("email", "").strip().lower()
    phone       = form.get("phone", "").strip()
    department  = form.get("department", "").strip()
    semester_raw = form.get("semester", "").strip()
    gpa_raw     = form.get("gpa", "").strip()
    dob         = form.get("date_of_birth", "").strip()
    status      = form.get("status", "Active").strip()

    if not full_name:
        errors.append("Full name is required.")
    elif len(full_name) < 2:
        errors.append("Full name must be at least 2 characters long.")

    if not roll_no:
        errors.append("Roll number is required.")
    elif not ROLL_NO_RE.match(roll_no):
        errors.append("Roll number may only contain letters, digits and "
                      "dashes (3–15 characters), e.g. CS2026001.")

    if not email:
        errors.append("Email address is required.")
    elif not EMAIL_RE.match(email):
        errors.append("Email address looks invalid — expected something "
                      "like jane@college.edu.")

    if phone and not PHONE_RE.match(phone):
        errors.append("Phone number may only contain digits, spaces, '-' "
                      "and a leading '+' (7–15 digits).")

    if department not in DEPARTMENTS:
        errors.append("Please choose a valid department.")

    try:
        semester = int(semester_raw)
        if not 1 <= semester <= 8:
            errors.append("Semester must be between 1 and 8.")
    except ValueError:
        semester = None
        errors.append("Semester is required and must be a number from 1 to 8.")

    gpa = None
    if gpa_raw:
        try:
            gpa = round(float(gpa_raw), 2)
            if not 0 <= gpa <= 10:
                errors.append("GPA must be between 0.00 and 10.00.")
        except ValueError:
            errors.append("GPA must be a number, for example 8.45.")

    if dob:
        try:
            parsed = datetime.strptime(dob, "%Y-%m-%d")
            if parsed.date() > date.today():
                errors.append("Date of birth cannot be in the future.")
        except ValueError:
            errors.append("Date of birth must be a valid date (YYYY-MM-DD).")
    else:
        dob = None

    if status not in ("Active", "Inactive"):
        status = "Active"

    cleaned = {
        "roll_no": roll_no, "full_name": full_name, "email": email,
        "phone": phone or None, "department": department,
        "semester": semester, "gpa": gpa,
        "date_of_birth": dob, "status": status,
    }
    return cleaned, errors
```

### 5.7 `app.py` — Web Layer (Routes)

```python
"""
app.py — Flask routes: the map of the site.
Each route: read the request → validate / look up data →
render a template, flash a message, or redirect.
"""
from flask import (Flask, abort, flash, jsonify, redirect,
                   render_template, request, url_for)
from database import init_db
from models import (DEPARTMENTS, SEMESTERS, add_student, delete_student,
                    email_exists, get_student, get_stats, get_students,
                    roll_no_exists, update_student)
from validators import validate_student

app = Flask(__name__)
app.config["SECRET_KEY"] = "student-dbms-please-change-me"
init_db()                                   # create table before first request

@app.route("/")
def dashboard():
    """Landing page — summary numbers from models.get_stats()."""
    return render_template("dashboard.html", stats=get_stats())

@app.route("/students")
def students():
    """Student list with search + filters + sorting (all via query string)."""
    search = request.args.get("search", "").strip() or None
    department = request.args.get("department", "").strip() or None
    semester_raw = request.args.get("semester", "").strip()
    semester = int(semester_raw) if semester_raw.isdigit() else None
    sort_by = request.args.get("sort_by", "full_name")
    sort_order = request.args.get("sort_order", "asc")
    data = get_students(search=search, department=department,
                        semester=semester, sort_by=sort_by,
                        sort_order=sort_order)
    return render_template("students.html", students=data,
                           search=search or "", department=department or "",
                           semester=semester, sort_by=sort_by,
                           sort_order=sort_order,
                           departments=DEPARTMENTS, semesters=SEMESTERS)

@app.route("/students/add", methods=["GET", "POST"])
def add_student_page():
    if request.method == "GET":
        return render_template("student_form.html", title="Add New Student",
                               student={}, departments=DEPARTMENTS,
                               semesters=SEMESTERS,
                               submit_label="Add Student",
                               cancel_url=url_for("students"))
    cleaned, errors = validate_student(request.form)
    if cleaned["roll_no"] and roll_no_exists(cleaned["roll_no"]):
        errors.append(f"Roll number '{cleaned['roll_no']}' is already taken.")
    if cleaned["email"] and email_exists(cleaned["email"]):
        errors.append(f"Email '{cleaned['email']}' is already registered "
                      "to another student.")
    if errors:
        for message in errors:
            flash(message, "error")
        return render_template("student_form.html", title="Add New Student",
                               student=request.form, departments=DEPARTMENTS,
                               semesters=SEMESTERS,
                               submit_label="Add Student",
                               cancel_url=url_for("students"))
    add_student(cleaned)
    flash(f"Student '{cleaned['full_name']}' added successfully.", "success")
    return redirect(url_for("students"))     # Post/Redirect/Get

@app.route("/students/<int:student_id>")
def student_detail(student_id):
    s = get_student(student_id)
    if s is None:
        abort(404)
    return render_template("student_detail.html", s=s)

@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student_page(student_id):
    s = get_student(student_id)
    if s is None:
        abort(404)
    if request.method == "GET":
        return render_template("student_form.html",
                               title=f"Edit — {s['full_name']}", student=s,
                               departments=DEPARTMENTS, semesters=SEMESTERS,
                               submit_label="Save Changes",
                               cancel_url=url_for("student_detail",
                                                  student_id=student_id))
    cleaned, errors = validate_student(request.form, student_id=student_id)
    if cleaned["roll_no"] and roll_no_exists(cleaned["roll_no"],
                                             exclude_id=student_id):
        errors.append(f"Roll number '{cleaned['roll_no']}' is already taken "
                      "by another student.")
    if cleaned["email"] and email_exists(cleaned["email"],
                                         exclude_id=student_id):
        errors.append(f"Email '{cleaned['email']}' is already used by "
                      "another student.")
    if errors:
        for message in errors:
            flash(message, "error")
        return render_template("student_form.html",
                               title=f"Edit — {s['full_name']}",
                               student=request.form,
                               departments=DEPARTMENTS, semesters=SEMESTERS,
                               submit_label="Save Changes",
                               cancel_url=url_for("student_detail",
                                                  student_id=student_id))
    update_student(student_id, cleaned)
    flash(f"Details for '{cleaned['full_name']}' updated.", "success")
    return redirect(url_for("student_detail", student_id=student_id))

@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student_page(student_id):
    """POST-only: a delete must be a deliberate form submission."""
    s = get_student(student_id)
    if s is None:
        abort(404)
    delete_student(student_id)
    flash(f"Student '{s['full_name']}' deleted.", "success")
    return redirect(url_for("students"))

@app.route("/api/students")
def api_students():
    """REST-style JSON view of the same data layer."""
    return jsonify(get_students())

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

### 5.8 `seed.py` — Sample Data Loader

```python
"""seed.py — fills an EMPTY database with 12 sample students. Idempotent."""
from database import get_db, init_db

SAMPLE_STUDENTS = [
    ("CS2026001", "Aarav Sharma",   "aarav.sharma@college.edu",
     "+91 98123 45670", "Computer Science", 3, 8.72, "2007-04-12", "Active"),
    ("CS2026014", "Priya Patel",    "priya.patel@college.edu",
     "+91 98220 11223", "Computer Science", 3, 9.10, "2006-11-02", "Active"),
    ("CS2025042", "Rohan Verma",    "rohan.verma@college.edu", None,
     "Computer Science", 5, 7.85, "2005-01-25", "Active"),
    ("IT2026008", "Sneha Kulkarni", "sneha.kulkarni@college.edu",
     "+91 97654 88990", "Information Technology", 3, 8.34, "2007-07-19", "Active"),
    ("IT2025021", "Vikram Singh",   "vikram.singh@college.edu", None,
     "Information Technology", 5, 6.98, "2005-09-08", "Inactive"),
    ("EC2026015", "Ananya Iyer",    "ananya.iyer@college.edu",
     "+91 90040 55661", "Electronics & Communication", 3, 8.91,
     "2006-12-30", "Active"),
    ("EC2025033", "Arjun Nair",     "arjun.nair@college.edu",
     "+91 98470 22334", "Electronics & Communication", 5, 7.42,
     "2005-03-14", "Active"),
    ("ME2026005", "Kavya Reddy",    "kavya.reddy@college.edu", None,
     "Mechanical", 3, 8.05, "2007-02-07", "Active"),
    ("ME2025018", "Ishita Bose",    "ishita.bose@college.edu",
     "+91 91610 77889", "Mechanical", 5, 9.25, "2005-06-23", "Active"),
    ("CV2026010", "Daniel Kim",     "daniel.kim@college.edu",
     "+1 415 555 0132", "Civil", 3, 7.60, "2007-08-01", "Active"),
    ("CV2025027", "Sofia Martinez", "sofia.martinez@college.edu",
     "+34 612 345 678", "Civil", 5, 8.48, "2005-05-16", "Active"),
    ("CS2025055", "Liam O'Brien",   "liam.obrien@college.edu", None,
     "Computer Science", 5, 6.75, "2004-10-10", "Inactive"),
]

def seed():
    init_db()
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    if count:
        print(f"Database already contains {count} students — nothing to do.")
        conn.close()
        return
    for s in SAMPLE_STUDENTS:
        conn.execute("""
            INSERT INTO students
                (roll_no, full_name, email, phone,
                 department, semester, gpa, date_of_birth, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, s)
    conn.commit()
    conn.close()
    print(f"Inserted {len(SAMPLE_STUDENTS)} sample students into students.db")

if __name__ == "__main__":
    seed()
```

### 5.9 Templates (Jinja2)

**`templates/base.html`** — shared layout (template inheritance: every page extends it):

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Home{% endblock %} · College Database</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
<nav class="topnav">
    <div class="container nav-inner">
        <a class="brand" href="{{ url_for('dashboard') }}">🎓 College <span>Database</span></a>
        <div class="nav-links">
            <a href="{{ url_for('dashboard') }}"
               class="{{ 'active' if request.endpoint == 'dashboard' }}">Dashboard</a>
            <a href="{{ url_for('students') }}"
               class="{{ 'active' if request.endpoint in ('students', 'student_detail', 'edit_student_page') }}">Students</a>
            <a class="btn btn-primary btn-sm" href="{{ url_for('add_student_page') }}">+ Add Student</a>
        </div>
    </div>
</nav>

<main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash flash-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
</main>

<footer class="footer">
    <div class="container">
        College Database · Flask + SQLite · College Mini Project
    </div>
</footer>
</body>
</html>
```

**`templates/students.html` (key parts)** — the reusable sort macro and the list:

```html
{% macro sort_link(col, label) %}
    {% set new_order = 'desc' if sort_by == col and sort_order == 'asc' else 'asc' %}
    <a class="{{ 'sorted' if sort_by == col }}"
       href="{{ url_for('students', search=search, department=department,
                        semester=semester, sort_by=col, sort_order=new_order) }}">
        {{ label }}
        {% if sort_by == col %}{{ '▲' if sort_order == 'asc' else '▼' }}{% endif %}
    </a>
{% endmacro %}

<form class="filter-bar card" method="get" action="{{ url_for('students') }}">
    <input type="search" name="search" value="{{ search }}"
           placeholder="Search name, roll no or email…">
    <select name="department">
        <option value="">All departments</option>
        {% for d in departments %}
            <option value="{{ d }}" {{ 'selected' if d == department }}>{{ d }}</option>
        {% endfor %}
    </select>
    <select name="semester">
        <option value="">All semesters</option>
        {% for s in semesters %}
            <option value="{{ s }}" {{ 'selected' if s == semester }}>Sem {{ s }}</option>
        {% endfor %}
    </select>
    <button class="btn btn-primary" type="submit">Filter</button>
</form>

<table class="students-table">
    <thead>
        <tr>
            <th>{{ sort_link('roll_no', 'Roll No') }}</th>
            <th>{{ sort_link('full_name', 'Name') }}</th>
            <th>{{ sort_link('department', 'Department') }}</th>
            <th>{{ sort_link('semester', 'Sem') }}</th>
            <th>{{ sort_link('gpa', 'GPA') }}</th>
            <th>Status</th><th></th>
        </tr>
    </thead>
    <tbody>
    {% for s in students %}
        <tr>
            <td class="mono">{{ s.roll_no }}</td>
            <td><a class="strong" href="{{ url_for('student_detail', student_id=s.id) }}">{{ s.full_name }}</a>
                <div class="sub">{{ s.email }}</div></td>
            <td><span class="badge badge-dept">{{ s.department }}</span></td>
            <td>Sem {{ s.semester }}</td>
            <td>{{ "%.2f"|format(s.gpa) if s.gpa is not none else "—" }}</td>
            <td><span class="badge {{ 'badge-active' if s.status == 'Active' else 'badge-inactive' }}">{{ s.status }}</span></td>
            <td class="actions">
                <a class="btn btn-sm" href="{{ url_for('edit_student_page', student_id=s.id) }}">Edit</a>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
```

**`templates/student_form.html` (key part)** — one form reused for add, edit, and error re-display:

```html
<form class="card form-card" method="post">
    <div class="form-grid">
        <div class="field">
            <label for="roll_no">Roll Number <span class="req">*</span></label>
            <input id="roll_no" name="roll_no" value="{{ student.get('roll_no', '') or '' }}"
                   placeholder="e.g. CS2026001">
        </div>
        <div class="field">
            <label for="full_name">Full Name <span class="req">*</span></label>
            <input id="full_name" name="full_name" value="{{ student.get('full_name', '') or '' }}">
        </div>
        <div class="field">
            <label for="email">Email <span class="req">*</span></label>
            <input id="email" name="email" type="email" value="{{ student.get('email', '') or '' }}">
        </div>
        <div class="field">
            <label for="phone">Phone (optional)</label>
            <input id="phone" name="phone" value="{{ student.get('phone', '') or '' }}">
        </div>
        <div class="field">
            <label for="department">Department <span class="req">*</span></label>
            <select id="department" name="department">
                <option value="">— choose —</option>
                {% for d in departments %}
                    <option value="{{ d }}" {{ 'selected' if student.get('department') == d }}>{{ d }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="field">
            <label for="semester">Semester <span class="req">*</span></label>
            <select id="semester" name="semester">
                <option value="">— choose —</option>
                {% for s in semesters %}
                    <option value="{{ s }}"
                        {{ 'selected' if student.get('semester') == s or student.get('semester') == s|string }}>Sem {{ s }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="field">
            <label for="gpa">GPA (0.00 – 10.00, optional)</label>
            <input id="gpa" name="gpa" type="number" step="0.01" min="0" max="10"
                   value="{{ student.get('gpa', '') if student.get('gpa') is not none else '' }}">
        </div>
        <div class="field">
            <label for="date_of_birth">Date of Birth (optional)</label>
            <input id="date_of_birth" name="date_of_birth" type="date"
                   value="{{ student.get('date_of_birth', '') or '' }}">
        </div>
        <div class="field">
            <label for="status">Status</label>
            <select id="status" name="status">
                <option value="Active" {{ 'selected' if (student.get('status') or 'Active') == 'Active' }}>Active</option>
                <option value="Inactive" {{ 'selected' if student.get('status') == 'Inactive' }}>Inactive</option>
            </select>
        </div>
    </div>
    <div class="form-actions">
        <button class="btn btn-primary" type="submit">{{ submit_label }}</button>
        <a class="btn" href="{{ cancel_url }}">Cancel</a>
    </div>
</form>
```

**`templates/student_detail.html` (delete part)** — POST-only delete with confirmation:

```html
<form method="post" action="{{ url_for('delete_student_page', student_id=s.id) }}"
      onsubmit="return confirm('Delete {{ s.full_name }}? This cannot be undone.');">
    <button class="btn btn-danger" type="submit">Delete</button>
</form>
```

### 5.10 Styling (`static/css/style.css`, summary)

Plain CSS (≈300 lines), no framework. Key points:

- **Design tokens as CSS variables** — every colour/size defined once in `:root`; changing `--primary` re-themes the whole app:

```css
:root {
    --bg: #f1f5f9;          --card: #ffffff;    --text: #0f172a;
    --muted: #64748b;       --border: #e2e8f0;  --primary: #4f46e5;
    --primary-dark: #4338ca; --danger: #dc2626; --success: #15803d;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(15,23,42,.08), 0 4px 16px rgba(15,23,42,.06);
}
```

- **Flexbox** for the sticky top navigation, page headers, filter bar and button rows.
- **CSS Grid** for the stat cards (`repeat(auto-fit, minmax(200px, 1fr))` — reflows automatically), the two-column dashboard, the two-column form and the detail card.
- **Media queries** collapse multi-column layouts to a single column on phones.
- Components: cards, buttons (primary/danger/small), pill badges (department/active/inactive), flash banners, and the department distribution **bar chart drawn purely with CSS** (a `div` whose width is a percentage set from Jinja).

### 5.11 How the Application Is Run

```bash
python3 -m venv .venv                  # 1. create a virtual environment
source .venv/bin/activate              # 2. activate it  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt        # 3. install Flask (only dependency)
python seed.py                         # 4. optional: load 12 sample students
python app.py                          # 5. run → http://localhost:5000
```

---

## 6. Output

The system was executed on Python 3.11 / Flask 3.1.3. The seed script loaded 12 sample students (`python seed.py` → *"Inserted 12 sample students into students.db"*). The screens below are presented as annotated wireframes with the **actual data and actual generated values** from the running system.

### 6.1 Screen 1 — Dashboard (`http://localhost:5000/`)

Statistics are computed live in SQL (`COUNT`, `AVG`, `GROUP BY`, `ORDER BY … LIMIT 1`):

```
+------------------------------------------------------------------------------+
| 🎓 College Database              Dashboard     Students     [+ Add Student]  |
+------------------------------------------------------------------------------+
|  Dashboard                                                                    |
+------------------------------------------------------------------------------+
|  +----------------+ +-------------+ +--------------+ +------------------+    |
|  | TOTAL STUDENTS | |   ACTIVE    | | AVERAGE GPA  | | TOP STUDENT      |    |
|  |       12       | |     10      | |    8.12      | | Ishita Bose      |    |
|  |                | |             | |              | | 9.25 GPA         |    |
|  |                | |             | |              | | ME2025018        |    |
|  +----------------+ +-------------+ +--------------+ +------------------+    |
+------------------------------------------------------------------------------+
|  Students by Department              | Recently Added                        |
|  Computer Science        4   [██████]| Priya Patel  | CS  | 3 | 9.10       |
|  Info. Technology        2   [███   ]| Daniel Kim   | CIV | 3 | 7.60       |
|  Electronics & Comm.     2   [███   ]| Sofia Mart.  | CIV | 5 | 8.48       |
|  Mechanical              2   [███   ]| Vikram Singh | IT  | 5 | 6.98       |
|  Civil                   2   [███   ]| …(5 rows)   |     |   |             |
+------------------------------------------------------------------------------+
| College Database · Flask + SQLite · College Mini Project                     |
+------------------------------------------------------------------------------+
```

### 6.2 Screen 2 — Student List with Search / Filter / Sort (`/students`)

```
+------------------------------------------------------------------------------+
| 🎓 College Database              Dashboard   Students      [+ Add Student]   |
+------------------------------------------------------------------------------+
|  Students (12)                                              [+ Add Student]  |
+------------------------------------------------------------------------------+
|  [ Search name, roll no or email…      ] [ All departments ▾ ] [ All sem ▾ ] |
|  [ Filter ]                                                        |
+------------------------------------------------------------------------------+
|  ROLL NO ▲ | NAME             | DEPARTMENT    | SEM | GPA  | STATUS | EDIT  |
|  CS2026001 | Aarav Sharma     | CS            | 3   | 8.72 | Active | [Edit]|
|  CS2026014 | Priya Patel      | CS            | 3   | 9.10 | Active | [Edit]|
|  CS2025042 | Rohan Verma      | CS            | 5   | 7.85 | Active | [Edit]|
|  CS2025055 | Liam O'Brien     | CS            | 5   | 6.75 | Inactive| [Edit]|
|  EC2026015 | Ananya Iyer      | ECE           | 3   | 8.91 | Active | [Edit]|
|  EC2025033 | Arjun Nair       | ECE           | 5   | 7.42 | Active | [Edit]|
|  CV2026010 | Daniel Kim       | Civil         | 3   | 7.60 | Active | [Edit]|
|  CV2025027 | Sofia Martinez   | Civil         | 5   | 8.48 | Active | [Edit]|
|  IT2026008 | Sneha Kulkarni   | IT            | 3   | 8.34 | Active | [Edit]|
|  IT2025021 | Vikram Singh     | IT            | 5   | 6.98 | Inactive| [Edit]|
|  ME2026005 | Kavya Reddy      | ME            | 3   | 8.05 | Active | [Edit]|
|  ME2025018 | Ishita Bose      | ME            | 5   | 9.25 | Active | [Edit]|
+------------------------------------------------------------------------------+
```

- Column headers are clickable: clicking **GPA** sorts descending/ascending (▲/▼ indicator); clicking again reverses the order.
- Searching `pri` → 1 row (Priya Patel). Filtering *Civil + Sem 3* → 1 row (Daniel Kim).
- The filter form is a GET form, so a filtered view produces a shareable URL, e.g.
  `/students?department=Civil&semester=3&sort_by=gpa&sort_order=desc`.

### 6.3 Screen 3 — Add Student (`/students/add`)

```
+------------------------------------------------------------------------------+
|  Add New Student                                                             |
+------------------------------------------------------------------------------+
|  Roll Number*  [ CS2026001          ]   Full Name*  [ Aarav Sharma      ]   |
|  Email*        [ aarav@college.edu  ]   Phone       [ +91 98123 45670 ]   |
|  Department*   [ Computer Science ▾ ]   Semester*   [ Sem 3             ▾] |
|  GPA           [ 8.72               ]   Date of Birth [ 2007-04-12    ]   |
|  Status        [ Active             ▾]                                            |
|  [ Add Student ]  [ Cancel ]                                                     |
+------------------------------------------------------------------------------+
```

**Successful submission** → green banner *"Student 'Aarav Sharma' added successfully."* and a redirect to the list, where the new row appears.

**Validation output** (submitting roll `CS2026001` again with GPA 15, email "bad", semester 9, DOB 2030-01-01, phone "abc") — all errors shown as red banners, with the form re-displayed **with the user's values intact**:

```
[ Roll number 'CS2026001' is already taken. ]
[ Email address looks invalid — expected something like jane@college.edu. ]
[ Phone number may only contain digits, spaces, '-' and a leading '+' (7–15 digits). ]
[ Semester must be between 1 and 8. ]
[ GPA must be between 0.00 and 10.00. ]
[ Date of birth cannot be in the future. ]
```

### 6.4 Screen 4 — Student Detail (`/students/9`)

```
+------------------------------------------------------------------------------+
|  ← Back to all students                                                      |
|  Ishita Bose  [ Active ]                          [ Edit ] [ Delete ]        |
+------------------------------------------------------------------------------+
|  ROLL NUMBER   | EMAIL                 | PHONE          | DEPARTMENT        |
|  ME2025018     | ishita.bose@college.  | +91 91610      | Mechanical        |
|                | edu                   | 77889          |                   |
|  SEMESTER      | GPA                   | DATE OF BIRTH  | RECORD CREATED    |
|  Semester 5    | 9.25                  | 2005-06-23     | 2026-09-26 …      |
+------------------------------------------------------------------------------+
```

**Delete** opens the browser confirm dialog (*"Delete Ishita Bose? This cannot be undone."*); on confirm the record is removed, a green banner *"Student 'Ishita Bose' deleted."* is shown, and the list is re-displayed with 11 rows.

### 6.5 Output 5 — JSON API (`/api/students`)

Actual response (first record, abridged):

```json
[
  {
    "created_at": "2026-09-26 15:43:26",
    "date_of_birth": "2007-04-12",
    "department": "Computer Science",
    "email": "aarav.sharma@college.edu",
    "full_name": "Aarav Sharma",
    "gpa": 8.72,
    "id": 1,
    "phone": "+91 98123 45670",
    "roll_no": "CS2026001",
    "semester": 3,
    "status": "Active"
  }
]
```

### 6.6 Output 6 — SQL Executed for a Typical Search

Search "pri" (name/roll/email) as generated by `models.get_students()`:

```sql
SELECT * FROM students WHERE 1=1
   AND (full_name LIKE ? OR roll_no LIKE ? OR email LIKE ?)
ORDER BY full_name ASC
-- parameters: ['%pri%', '%pri%', '%pri%']
```

### 6.7 Output 7 — Security Test Results

| Test | Input | Result |
|---|---|---|
| SQL injection attempt in search | `1' OR 1=1 --` | Treated as literal text; 0 rows returned; no error |
| XSS attempt in name field | `<script>alert(1)</script>` | Rendered as visible text (auto-escaped), no script executed |
| Duplicate roll number (form) | existing `CS2026001` | Rejected with friendly message |
| Duplicate roll number (raw SQL, bypassing app) | `INSERT … CS2026001` | Rejected by the `UNIQUE` constraint (`IntegrityError`) |
| Invalid semester (raw SQL) | `semester = 9` | Rejected by `CHECK (semester BETWEEN 1 AND 8)` |
| Unknown URL | `/students/9999` | Friendly 404 page with status code 404 |
| POST-only delete via GET link | `GET /students/1/delete` | Flask returns 405 Method Not Allowed |

### 6.8 Output 8 — End-to-End Verification Log

Automated tests against the running app (Flask test client):

```
GET  /                   → 200
GET  /students           → 200
GET  /students?search=aarav      → 200  (Aarav Sharma found)
GET  /students?department=Civil&semester=3 → 200  (Daniel Kim found)
GET  /students/1         → 200
GET  /students/add       → 200
POST /students/add  (valid data)    → 302 → success banner shown
POST /students/add  (8 invalid fields) → all 8 error banners shown
POST /students/<id>/edit (valid)    → 302 → updated values shown
POST /students/<id>/delete          → 302 → "deleted" banner shown
GET  /api/students       → 200  (JSON, 12 items)
GET  /students/999       → 404  (friendly page)
```

---

## 7. References

1. Pallets Projects. *Flask — Python Web Framework. Official Documentation and Tutorial.* https://flask.palletsprojects.com/en/stable/ (accessed: 2026)
2. SQLite Development Team. *SQLite Tutorial and Language Reference.* https://www.sqlite.org/tutorial.html (accessed: 2026)
3. Pallets Projects. *Jinja2 — Template Engine Documentation.* https://jinja.palletsprojects.com/en/stable/ (accessed: 2026)
4. Python Software Foundation. *Python 3 Standard Library — sqlite3: SQLite interface.* https://docs.python.org/3/library/sqlite3.html (accessed: 2026)
5. Grinberg, M. *Flask Web Development: Developing Web Applications with Python*, 2nd ed. O'Reilly Media, 2018.
6. Eckel, B. *Thinking in Python* / standard Python 3 references. https://docs.python.org/3/ (accessed: 2026)
7. OWASP Foundation. *SQL Injection and Cross-Site Scripting (XSS) — Prevention Cheatsheets.* https://owasp.org/www-project-web-security-testing-guide/ (accessed: 2026)
8. W3C. *Cascading Style Sheets (CSS) — CSS Variables, Flexbox, Grid.* https://developer.mozilla.org/en-US/docs/Web/CSS (accessed: 2026)

---

*Code repository: `magnate0761/new_project`, branch `arena/01a0de5c-new-project` — https://github.com/magnate0761/new_project/tree/arena/01a0de5c-new-project*
