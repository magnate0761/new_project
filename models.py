"""
models.py
=========
The *data layer* — the only file in the project that writes SQL.

The web layer (app.py) never touches SQL directly; it calls these
functions instead.  So app.py stays about *web logic* (routes, form
handling, messages) and models.py stays about *database logic*.

Every public function here follows the same small pattern:

    1. open a connection            conn = get_db()
    2. run a SQL statement          conn.execute(...)
    3. fetch what you need          .fetchone() / .fetchall()
    4. close the connection         conn.close()
"""

from database import get_db

# ---------------------------------------------------------------------------
# Constants shared by forms, filters and the database
# ---------------------------------------------------------------------------
DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Electronics & Communication",
    "Mechanical",
    "Civil",
]
SEMESTERS = list(range(1, 9))  # [1, 2, 3, 4, 5, 6, 7, 8]

# Columns the user is allowed to sort the student table by (a *whitelist*).
# SQL can't be built from arbitrary user input — see get_students().
SORTABLE = {"full_name", "roll_no", "department", "semester", "gpa", "created_at"}


# ---------------------------------------------------------------------------
# Reading data
# ---------------------------------------------------------------------------
def get_students(search=None, department=None, semester=None,
                 sort_by="full_name", sort_order="asc"):
    """Return a list of students (as dicts), filtered by any combination
    of: free-text search, department and semester.

    `?` are *placeholders* — their values are filled from the `params`
    list.  Because values are sent separately from the SQL text, this is
    what protects the app from SQL injection.
    """
    conn = get_db()

    # `WHERE 1=1` is a small trick: 1 is always true, so the query is
    # valid on its own, and we can just append " AND …" pieces to it.
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        query += " AND (full_name LIKE ? OR roll_no LIKE ? OR email LIKE ?)"
        like = f"%{search}%"          # % = "any number of characters"
        params += [like, like, like]

    if department:
        query += " AND department = ?"
        params.append(department)

    if semester:
        query += " AND semester = ?"
        params.append(semester)

    # The sort *column name* cannot be a ? placeholder (SQL doesn't allow
    # placeholders for identifiers), so instead we only accept names that
    # are on our SORTABLE whitelist.  Anything else falls back to a safe
    # default.  This keeps the ordering clause safe too.
    if sort_by not in SORTABLE:
        sort_by = "full_name"
    order = "DESC" if sort_order == "desc" else "ASC"
    query += f" ORDER BY {sort_by} {order}"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    # Convert each row to a plain dict — easier to work with in templates
    # and to send as JSON from the API route.
    return [dict(r) for r in rows]


def get_student(student_id):
    """Return one student by primary key, or None if it doesn't exist."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    """Compute every number the dashboard needs, in one round trip each.

    Returns a dict with:
        total            -> number of rows
        active           -> rows with status = 'Active'
        avg_gpa          -> average of non-NULL gpa values (None if empty)
        top              -> highest-GPA student (dict or None)
        departments      -> [(department, count), …] most-populated first
        recent           -> last 5 students added
        max_dept_count   -> biggest department count (used to size the bars)
    """
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    active = conn.execute(
        "SELECT COUNT(*) AS c FROM students WHERE status = 'Active'"
    ).fetchone()["c"]
    avg_gpa = conn.execute(
        "SELECT AVG(gpa) AS a FROM students WHERE gpa IS NOT NULL"
    ).fetchone()["a"]
    top = conn.execute(
        """
        SELECT roll_no, full_name, gpa
        FROM students
        WHERE gpa IS NOT NULL
        ORDER BY gpa DESC, full_name ASC
        LIMIT 1
        """
    ).fetchone()
    departments = [
        dict(r) for r in conn.execute(
            """
            SELECT department, COUNT(*) AS count
            FROM students
            GROUP BY department
            ORDER BY count DESC
            """
        ).fetchall()
    ]
    recent = [
        dict(r) for r in conn.execute(
            """
            SELECT id, roll_no, full_name, department, semester, gpa, status
            FROM students
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()
    ]

    conn.close()

    max_dept_count = max((d["count"] for d in departments), default=0)
    return {
        "total": total,
        "active": active,
        "avg_gpa": avg_gpa,
        "top": dict(top) if top else None,
        "departments": departments,
        "recent": recent,
        "max_dept_count": max_dept_count,
    }


# ---------------------------------------------------------------------------
# Uniqueness checks (used by app.py when validating forms)
# ---------------------------------------------------------------------------
def roll_no_exists(roll_no, exclude_id=None):
    """True if roll_no is already in the table.

    When *editing*, pass exclude_id so the student's own roll number
    doesn't count as a conflict.
    """
    conn = get_db()
    query = "SELECT 1 FROM students WHERE roll_no = ?"
    params = [roll_no]
    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row is not None


def email_exists(email, exclude_id=None):
    """Same idea as roll_no_exists(), but for the email column."""
    conn = get_db()
    query = "SELECT 1 FROM students WHERE email = ?"
    params = [email]
    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row is not None


# ---------------------------------------------------------------------------
# Writing data  (Create / Update / Delete — the CUD of CRUD)
# ---------------------------------------------------------------------------
def add_student(data):
    """Insert one student.  `data` is the validated dict from validators.py.
    Returns the id SQLite assigned to the new row."""
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO students
            (roll_no, full_name, email, phone,
             department, semester, gpa, date_of_birth, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["roll_no"], data["full_name"], data["email"],
            data["phone"], data["department"], data["semester"],
            data["gpa"], data["date_of_birth"], data["status"],
        ),
    )
    conn.commit()          # commit = "make it permanent on disk"
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_student(student_id, data):
    """Update the row with this id.  Returns True if a row was changed."""
    conn = get_db()
    cur = conn.execute(
        """
        UPDATE students
        SET roll_no       = ?,
            full_name     = ?,
            email         = ?,
            phone         = ?,
            department    = ?,
            semester      = ?,
            gpa           = ?,
            date_of_birth = ?,
            status        = ?
        WHERE id = ?
        """,
        (
            data["roll_no"], data["full_name"], data["email"],
            data["phone"], data["department"], data["semester"],
            data["gpa"], data["date_of_birth"], data["status"],
            student_id,
        ),
    )
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


def delete_student(student_id):
    """Delete the row with this id.  Returns True if a row was removed."""
    conn = get_db()
    cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    removed = cur.rowcount > 0
    conn.close()
    return removed
