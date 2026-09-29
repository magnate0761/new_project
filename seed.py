"""
seed.py
=======
Optional helper: fills the (empty) database with a handful of sample
students so the app is interesting to look at right away.

Run it with:
    python seed.py

Safe to run repeatedly — it only inserts when the table is empty.
To start over from scratch: stop the app, delete students.db, re-run this.
"""

from database import get_db, init_db

# The fields line up with the columns in database.init_db()
SAMPLE_STUDENTS = [
    ("CS2026001", "Aarav Sharma",   "aarav.sharma@college.edu",   "+91 98123 45670", "Computer Science",              3, 8.72, "2007-04-12", "Active"),
    ("CS2026014", "Priya Patel",    "priya.patel@college.edu",    "+91 98220 11223", "Computer Science",              3, 9.10, "2006-11-02", "Active"),
    ("CS2025042", "Rohan Verma",    "rohan.verma@college.edu",    None,              "Computer Science",              5, 7.85, "2005-01-25", "Active"),
    ("IT2026008", "Sneha Kulkarni", "sneha.kulkarni@college.edu", "+91 97654 88990", "Information Technology",        3, 8.34, "2007-07-19", "Active"),
    ("IT2025021", "Vikram Singh",   "vikram.singh@college.edu",   None,              "Information Technology",        5, 6.98, "2005-09-08", "Inactive"),
    ("EC2026015", "Ananya Iyer",    "ananya.iyer@college.edu",    "+91 90040 55661", "Electronics & Communication",   3, 8.91, "2006-12-30", "Active"),
    ("EC2025033", "Arjun Nair",     "arjun.nair@college.edu",     "+91 98470 22334", "Electronics & Communication",   5, 7.42, "2005-03-14", "Active"),
    ("ME2026005", "Kavya Reddy",    "kavya.reddy@college.edu",    None,              "Mechanical",                    3, 8.05, "2007-02-07", "Active"),
    ("ME2025018", "Ishita Bose",    "ishita.bose@college.edu",    "+91 91610 77889", "Mechanical",                    5, 9.25, "2005-06-23", "Active"),
    ("CV2026010", "Daniel Kim",     "daniel.kim@college.edu",     "+1 415 555 0132", "Civil",                         3, 7.60, "2007-08-01", "Active"),
    ("CV2025027", "Sofia Martinez", "sofia.martinez@college.edu", "+34 612 345 678", "Civil",                         5, 8.48, "2005-05-16", "Active"),
    ("CS2025055", "Liam O'Brien",   "liam.obrien@college.edu",    None,              "Computer Science",              5, 6.75, "2004-10-10", "Inactive"),
]


def seed():
    init_db()
    conn = get_db()

    # Already has rows? Nothing to do.
    count = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    if count:
        print(f"Database already contains {count} students — nothing to do.")
        conn.close()
        return

    for s in SAMPLE_STUDENTS:
        conn.execute(
            """
            INSERT INTO students
                (roll_no, full_name, email, phone,
                 department, semester, gpa, date_of_birth, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            s,
        )
    conn.commit()
    conn.close()
    print(f"Inserted {len(SAMPLE_STUDENTS)} sample students into students.db")


if __name__ == "__main__":
    seed()
