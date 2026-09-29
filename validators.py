"""
validators.py
=============
Form validation, checked *in Python before anything reaches the database*.

The database has its own constraints (UNIQUE, CHECK …) as a last line of
defence, but users deserve friendly, specific error messages — and those
can only be produced here, in Python.

The one public function is validate_student():
    * takes the raw form submission (a dict-like object),
    * returns (cleaned, errors):
        cleaned  -> a dict with properly typed values, ready to be stored
        errors   -> a list of human-readable problems (empty if all good)
"""

import re
from datetime import date, datetime

from models import DEPARTMENTS

# Regular expressions — small "pattern languages" for text checks.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
#    something@something.something — at least one char each side, one dot
PHONE_RE = re.compile(r"^\+?[0-9\s\-]{7,15}$")
#    optional leading '+', then 7–15 chars of digits / spaces / dashes
ROLL_NO_RE = re.compile(r"^[A-Z0-9\-]{3,15}$")
#    letters, digits or dashes only, 3–15 chars (normalised to UPPER first)


def validate_student(form, student_id=None):
    """Validate a submitted student form.

    `form` is a dict-like object (Flask's request.form).
    When *editing* an existing student, pass its id so that uniqueness
    checks elsewhere ignore the student's own roll number / email.
    """
    errors = []

    # ------------------------------------------------------------------
    # Read + normalise every field (strip stray spaces, fix case, …)
    # ------------------------------------------------------------------
    roll_no = form.get("roll_no", "").strip().upper()
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip().lower()
    phone = form.get("phone", "").strip()
    department = form.get("department", "").strip()
    semester_raw = form.get("semester", "").strip()
    gpa_raw = form.get("gpa", "").strip()
    dob = form.get("date_of_birth", "").strip()
    status = form.get("status", "Active").strip()

    # ------------------------------------------------------------------
    # Required text fields
    # ------------------------------------------------------------------
    if not full_name:
        errors.append("Full name is required.")
    elif len(full_name) < 2:
        errors.append("Full name must be at least 2 characters long.")

    if not roll_no:
        errors.append("Roll number is required.")
    elif not ROLL_NO_RE.match(roll_no):
        errors.append(
            "Roll number may only contain letters, digits and dashes "
            "(3–15 characters), e.g. CS2026001."
        )

    if not email:
        errors.append("Email address is required.")
    elif not EMAIL_RE.match(email):
        errors.append(
            "Email address looks invalid — expected something like "
            "jane@college.edu."
        )

    # Phone is optional, but if present it must look like a phone number.
    if phone and not PHONE_RE.match(phone):
        errors.append(
            "Phone number may only contain digits, spaces, '-' and a "
            "leading '+' (7–15 digits)."
        )

    # ------------------------------------------------------------------
    # Department & semester
    # ------------------------------------------------------------------
    if department not in DEPARTMENTS:
        errors.append("Please choose a valid department.")

    try:
        semester = int(semester_raw)
        if not 1 <= semester <= 8:
            errors.append("Semester must be between 1 and 8.")
    except ValueError:
        semester = None  # leave as None so add/update still has a value
        errors.append("Semester is required and must be a number from 1 to 8.")

    # ------------------------------------------------------------------
    # GPA — optional, must be a number in 0.00 … 10.00
    # ------------------------------------------------------------------
    gpa = None
    if gpa_raw:
        try:
            gpa = round(float(gpa_raw), 2)
            if not 0 <= gpa <= 10:
                errors.append("GPA must be between 0.00 and 10.00.")
        except ValueError:
            errors.append("GPA must be a number, for example 8.45.")

    # ------------------------------------------------------------------
    # Date of birth — optional, must be a real date and not in the future
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Package the cleaned, typed values for the database layer
    # ------------------------------------------------------------------
    cleaned = {
        "roll_no": roll_no,
        "full_name": full_name,
        "email": email,
        "phone": phone or None,
        "department": department,
        "semester": semester,
        "gpa": gpa,
        "date_of_birth": dob,
        "status": status,
    }
    return cleaned, errors
