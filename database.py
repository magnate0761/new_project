"""
database.py
===========
Everything about *connecting* to the SQLite database lives here.

Why a separate file?
--------------------
Other files (models.py, app.py) only ever *ask* this file for a connection.
That means if you ever moved from SQLite to MySQL/PostgreSQL, you would only
have to change THIS file — not every query in the whole project.
(This idea is called "separation of concerns".)

SQLite stores the entire database in a single file on disk (students.db),
so you never need to install or start a database server.
"""

import os
import sqlite3

# Directory where this file lives (…/new_project), no matter where the
# app is started from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# …so the database file is always created *next to the code*.
DB_PATH = os.path.join(BASE_DIR, "students.db")


def get_db():
    """Open a fresh SQLite connection and return it.

    `sqlite3.Row` makes every result row behave like a dictionary AND like
    an object:  row["full_name"]  and  row.full_name  both work.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the table (and its indexes) if they do not exist yet.

    Called once at startup from app.py.  `IF NOT EXISTS` makes the call
    safe to repeat — it never touches data that is already stored.
    """
    conn = get_db()
    conn.execute(
        """
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
        """
    )
    # Indexes let SQLite find rows quickly without scanning the whole table.
    # They matter a lot once the table has hundreds or thousands of rows.
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_students_name "
        "ON students (full_name)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_students_dept "
        "ON students (department)"
    )
    conn.commit()
    conn.close()
