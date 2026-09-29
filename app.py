"""
app.py
======
The *web layer* — Flask routes (URLs) and page logic.

Flask is a "micro" web framework: you give it a URL (a *route*) and a
function to run when that URL is visited.  The function returns either:
    * HTML  -> render_template() renders a Jinja2 file and sends it back
    * a redirect -> redirect(url_for(...)) bounces the browser to another page
    * JSON  -> jsonify(...) for the little API at /api/students

Every route below shows the same small dance:

    1. read the request  (request.form / request.args / URL parameters)
    2. validate / look up data
    3. render a template, flash a message, or redirect
"""

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from database import init_db
from models import (
    DEPARTMENTS,
    SEMESTERS,
    add_student,
    delete_student,
    email_exists,
    get_student,
    get_stats,
    get_students,
    roll_no_exists,
    update_student,
)
from validators import validate_student

app = Flask(__name__)

# Flask signs the session cookie (which carries flash messages) with this
# key.  Any hard-coded string works for a college project — just don't
# ship it unchanged to a real production server.
app.config["SECRET_KEY"] = "student-dbms-please-change-me"

# Make sure the table exists before the first request is served.
init_db()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    """Landing page.  All the summary numbers are computed by
    models.get_stats() and dropped into the template as `stats`."""
    return render_template("dashboard.html", stats=get_stats())


# ---------------------------------------------------------------------------
# Student list (with search, filters, sorting)
# ---------------------------------------------------------------------------
@app.route("/students")
def students():
    """The main student table.

    All controls arrive via the *query string* (?search=…&department=…)
    because the filter bar is a GET form.  GET is the right choice here:
    filters should be shareable/bookmarkable URLs, and GET never changes
    data, so it is safe to repeat or send to a friend.
    """
    search = request.args.get("search", "").strip() or None
    department = request.args.get("department", "").strip() or None

    semester_raw = request.args.get("semester", "").strip()
    semester = int(semester_raw) if semester_raw.isdigit() else None

    sort_by = request.args.get("sort_by", "full_name")
    sort_order = request.args.get("sort_order", "asc")

    data = get_students(
        search=search,
        department=department,
        semester=semester,
        sort_by=sort_by,          # models.py keeps this safe (whitelist)
        sort_order=sort_order,
    )

    return render_template(
        "students.html",
        students=data,
        search=search or "",
        department=department or "",
        semester=semester,
        sort_by=sort_by,
        sort_order=sort_order,
        departments=DEPARTMENTS,
        semesters=SEMESTERS,
    )


# ---------------------------------------------------------------------------
# Add a student   (Create in CRUD)
# ---------------------------------------------------------------------------
@app.route("/students/add", methods=["GET", "POST"])
def add_student_page():
    if request.method == "GET":
        # Show an empty form.
        return render_template(
            "student_form.html",
            title="Add New Student",
            student={},
            departments=DEPARTMENTS,
            semesters=SEMESTERS,
            submit_label="Add Student",
            cancel_url=url_for("students"),
        )

    # POST: a form was submitted.
    cleaned, errors = validate_student(request.form)

    # Uniqueness rules need a database lookup, so they live here.
    if cleaned["roll_no"] and roll_no_exists(cleaned["roll_no"]):
        errors.append(f"Roll number '{cleaned['roll_no']}' is already taken.")
    if cleaned["email"] and email_exists(cleaned["email"]):
        errors.append(f"Email '{cleaned['email']}' is already registered to another student.")

    if errors:
        # Flash each problem, then RE-RENDER the form with the values the
        # user typed (request.form) so nothing they entered is lost.
        for message in errors:
            flash(message, "error")
        return render_template(
            "student_form.html",
            title="Add New Student",
            student=request.form,
            departments=DEPARTMENTS,
            semesters=SEMESTERS,
            submit_label="Add Student",
            cancel_url=url_for("students"),
        )

    add_student(cleaned)
    flash(f"Student '{cleaned['full_name']}' added successfully.", "success")
    # "Post/Redirect/Get": after a POST, bounce the browser back to a GET
    # page.  If the user pressed Refresh, the form is not re-submitted.
    return redirect(url_for("students"))


# ---------------------------------------------------------------------------
# Student detail page (Read in CRUD)
# ---------------------------------------------------------------------------
@app.route("/students/<int:student_id>")
def student_detail(student_id):
    """One student's full profile.  <int:student_id> is a Flask converter —
    Flask only calls this route if the URL part is an integer."""
    s = get_student(student_id)
    if s is None:                      # e.g. /students/9999
        abort(404)                     # -> handled by the 404 handler below
    return render_template("student_detail.html", s=s)


# ---------------------------------------------------------------------------
# Edit a student  (Update in CRUD)
# ---------------------------------------------------------------------------
@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student_page(student_id):
    s = get_student(student_id)
    if s is None:
        abort(404)

    if request.method == "GET":
        # Show the same form as "add", pre-filled with the stored values.
        return render_template(
            "student_form.html",
            title=f"Edit — {s['full_name']}",
            student=s,
            departments=DEPARTMENTS,
            semesters=SEMESTERS,
            submit_label="Save Changes",
            cancel_url=url_for("student_detail", student_id=student_id),
        )

    # POST: validate exactly like adding, but pass student_id so the
    # uniqueness checks ignore this student's own roll no / email.
    cleaned, errors = validate_student(request.form, student_id=student_id)
    if cleaned["roll_no"] and roll_no_exists(cleaned["roll_no"], exclude_id=student_id):
        errors.append(f"Roll number '{cleaned['roll_no']}' is already taken by another student.")
    if cleaned["email"] and email_exists(cleaned["email"], exclude_id=student_id):
        errors.append(f"Email '{cleaned['email']}' is already used by another student.")

    if errors:
        for message in errors:
            flash(message, "error")
        return render_template(
            "student_form.html",
            title=f"Edit — {s['full_name']}",
            student=request.form,
            departments=DEPARTMENTS,
            semesters=SEMESTERS,
            submit_label="Save Changes",
            cancel_url=url_for("student_detail", student_id=student_id),
        )

    update_student(student_id, cleaned)
    flash(f"Details for '{cleaned['full_name']}' updated.", "success")
    return redirect(url_for("student_detail", student_id=student_id))


# ---------------------------------------------------------------------------
# Delete a student  (Delete in CRUD)
# ---------------------------------------------------------------------------
@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student_page(student_id):
    """POST only — a link could trigger a delete by accident (or via
    browser prefetching); a real form submission is a deliberate act.
    The template's confirm() dialog is the extra "are you sure?" step."""
    s = get_student(student_id)
    if s is None:
        abort(404)

    delete_student(student_id)
    flash(f"Student '{s['full_name']}' deleted.", "success")
    return redirect(url_for("students"))


# ---------------------------------------------------------------------------
# Tiny JSON API — the same data the table shows, machine-readable
# ---------------------------------------------------------------------------
@app.route("/api/students")
def api_students():
    """A minimal REST-style endpoint.  Handy to mention in the project
    report, and useful if you ever build a mobile app or a separate
    front-end.  Try it:  http://localhost:5000/api/students"""
    return jsonify(get_students())


# ---------------------------------------------------------------------------
# Friendly 404 page instead of Flask's default
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # host 0.0.0.0 -> reachable from other machines on the network (not just
    # this computer); port 5000 -> Flask's default.
    # debug=True -> if a page raises an error, Flask shows an interactive
    # debugger in the browser with the traceback.  Great while developing,
    # off in production.
    app.run(host="0.0.0.0", port=5000, debug=True)
