# 🎓 Student Database Management System

A complete, working web application for managing college student records —
built with **Python + Flask + SQLite**, styled with **plain CSS** (no
frameworks), and documented file-by-file so you can explain every line of it.

> A "database management system" in the everyday sense: an app that lets you
> **C**reate, **R**ead, **U**pdate and **D**elete (CRUD) student records and
> get quick statistics — with a database underneath.

---

## ✨ Features

| Feature | Where |
|---|---|
| Dashboard with totals, average GPA, top student, department distribution bar chart | `GET /` |
| Student table with **live search** (name / roll no / email) | `GET /students?search=…` |
| **Filter** by department and/or semester | same page |
| **Sort** by any column (click headers, click again to reverse) | same page |
| Add a student with full server-side validation | `GET/POST /students/add` |
| View a student's full profile | `GET /students/<id>` |
| Edit any field, with re-validation | `GET/POST /students/<id>/edit` |
| Delete with a confirmation dialog (POST-only route) | `POST /students/<id>/delete` |
| Tiny JSON API for machines | `GET /api/students` |
| Friendly 404 page | any unknown URL |
| Friendly error messages instead of blank failures | everywhere |
| Sample-data seeder so the demo is never empty | `python seed.py` |

## 🧰 Tech stack (and why)

| Technology | Role | Why it's a good choice for a college project |
|---|---|---|
| **Python 3** | language | readable, huge learning community |
| **Flask** | web framework | minimal and explicit — you see *exactly* what the framework does, unlike Django which hides a lot |
| **SQLite** | database | a real relational database that lives in **one file** (`students.db`) — no server to install or configure, and it speaks real SQL |
| **Jinja2** | templating | Flask's built-in HTML templating engine (`{{ }}`, `{% %}`) |
| **Plain CSS** | styling | no framework dependency; easy to explain and customise |

There is **one** third-party package: `flask` (listed in `requirements.txt`).
Everything else is Python's standard library — including `sqlite3`, which is
built into Python.

---

## 📁 Project structure

```
new_project/
├── app.py                  ← THE web layer: routes/URLs, form handling, messages
├── models.py               ← THE data layer: all SQL queries (the only file with SQL)
├── database.py             ← connection + table creation (schema lives here)
├── validators.py           ← form validation in Python (friendly error messages)
├── seed.py                 ← optional: inserts 12 sample students on an empty DB
├── requirements.txt        ← the one dependency: flask
├── .gitignore              ← keeps .venv/, __pycache__/ and students.db out of git
├── students.db             ← (created at first run) the actual database file
├── static/
│   └── css/style.css       ← all styling; colours defined once as CSS variables
└── templates/
    ├── base.html           ← shared layout: <nav>, flash banners, footer
    ├── dashboard.html      ← "/"   stat cards + charts
    ├── students.html       ← list + search + filters + sorting
    ├── student_form.html   ← shared by "add" AND "edit"
    ├── student_detail.html ← one student's profile + edit/delete buttons
    └── 404.html            ← friendly not-found page
```

### The 3-layer idea (the single most important concept)

```
 Browser (HTML/CSS/JS)
     │  HTTP request (GET /students?search=priya)
     ▼
 ┌─────────────┐   validates form    ┌─────────────────┐
 │   app.py    │ ──────────────────► │  validators.py  │
 │  (web layer)│                     └─────────────────┘
 └──────┬──────┘
        │  calls functions (no SQL here!)
        ▼
 ┌─────────────┐   executes SQL      ┌─────────────────┐
 │  models.py  │ ──────────────────► │ database.py     │ ──► students.db
 │(data layer) │                     │ (connection +   │
 └─────────────┘                     │  table schema)  │
                                     └─────────────────┘
```

- **app.py** knows about *websites* (URLs, forms, redirects) but never writes SQL.
- **models.py** knows about *data* (SQL) but never knows about websites.
- **database.py** knows how to *connect* — swap SQLite for MySQL here later, nothing else changes.

That separation is what makes the code understandable: each file has exactly one job.

---

## 🏃 How to run it

```bash
# 1. create a virtual environment (once)
python3 -m venv .venv

# 2. activate it
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. install the one dependency
pip install -r requirements.txt

# 4. (optional) load 12 sample students — only fills an EMPTY database
python seed.py

# 5. start the app
python app.py
```

Open **http://localhost:5000** in your browser.

**Start over / reset the data:** stop the app, delete `students.db`, re-run
`python seed.py`. (The DB file is data, not code — that's why it's in
`.gitignore`.)

---

## 🔄 What happens when you load the dashboard?

Tracing one request end-to-end:

1. **Browser** sends `GET /`.
2. **Flask** looks at its route table, sees `@app.route("/")`, calls `dashboard()`.
3. **`dashboard()`** calls `get_stats()` in *models.py*.
4. **`get_stats()`** opens a connection (`get_db()`), runs 5 SQL queries
   (`COUNT`, `AVG`, `GROUP BY` …), and returns one dict with all the numbers.
5. **`dashboard()`** calls `render_template("dashboard.html", stats=…)`.
6. **Jinja2** takes `templates/dashboard.html`, extends `base.html`, replaces
   every `{{ stats.total }}` with the real value, and produces plain HTML.
7. Flask sends the HTML back; the **browser** renders it with `style.css`.

Every other page follows the same dance — the only difference is which model
function is called and which template is filled in.

---

## 📄 File-by-file explanation

### `database.py` — the connection & the schema

- `BASE_DIR` / `DB_PATH`: compute the database file's path **relative to the
  script's own folder** (`os.path.dirname(os.path.abspath(__file__))`), so the
  app works no matter which directory you start it from.
- `get_db()`: `sqlite3.connect(DB_PATH)` opens the file (creating it if
  missing). `conn.row_factory = sqlite3.Row` makes result rows dict-like.
- `init_db()`: runs the `CREATE TABLE IF NOT EXISTS students (…)` statement.
  Read the column list there — **that IS the schema**:

  | column | type | constraint | meaning |
  |---|---|---|---|
  | `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | auto number, the row's unique identity |
  | `roll_no` | TEXT | NOT NULL **UNIQUE** | roll numbers can't be duplicated |
  | `full_name` | TEXT | NOT NULL | the student's name |
  | `email` | TEXT | NOT NULL **UNIQUE** | emails can't be duplicated |
  | `phone` | TEXT | *(nullable)* | optional |
  | `department` | TEXT | NOT NULL | one of the 5 fixed departments |
  | `semester` | INTEGER | NOT NULL, `CHECK (1–8)` | can only be 1…8 |
  | `gpa` | REAL | `CHECK (0–10)`, nullable | on a 10-point scale |
  | `date_of_birth` | TEXT | nullable | stored as `YYYY-MM-DD` |
  | `status` | TEXT | NOT NULL, `CHECK ('Active','Inactive')` | default `'Active'` |
  | `created_at` | TEXT | default `datetime('now')` | when the record was made |

  The `CHECK (…)` clauses are the database's *own* safety net — even if the
  Python validation were bypassed, impossible values can't be stored.
- Two `CREATE INDEX` statements on `full_name` and `department`: index pages
  that let SQLite jump straight to matching rows instead of scanning all rows.

### `models.py` — every SQL query

Every function follows: *open connection → execute → fetch → close*.

- **`get_students(search, department, semester, sort_by, sort_order)`** — the
  workhorse behind the list page. It builds the query in pieces:

  ```sql
  SELECT * FROM students WHERE 1=1
       AND (full_name LIKE ? OR roll_no LIKE ? OR email LIKE ?)   -- if searching
       AND department = ?                                         -- if filtered
       AND semester     = ?                                       -- if filtered
  ORDER BY full_name ASC                                          -- sorted
  ```

  * `WHERE 1=1` is a trick: `1=1` is always true, so the query is valid even
    with zero filters, and the optional pieces can just be appended with `AND`.
  * `?` **placeholders** are filled from the `params` list. The values never
    become part of the SQL text — the driver inserts them safely. **This is
    the project's protection against SQL injection.**
  * `LIKE '%text%'` = "contains text anywhere".
  * The sort *column name* can't be a `?` placeholder (SQL doesn't allow
    placeholders for column names), so `sort_by` is checked against the
    `SORTABLE` whitelist before it's inserted into the string. Anything not on
    the list falls back to `full_name`. A second common technique for keeping
    ORDER BY safe.
  * Rows come back as `sqlite3.Row` and are converted to plain `dict`s,
    which both the templates and the JSON API can consume directly.

- **`get_student(student_id)`** — `SELECT * … WHERE id = ?`; returns a dict or
  `None` (which app.py turns into a 404).
- **`get_stats()`** — 5 small aggregation queries for the dashboard:
  `COUNT(*)`, `COUNT(*) WHERE status='Active'`, `AVG(gpa)`, a top-student
  query with `ORDER BY gpa DESC LIMIT 1`, a `GROUP BY department` for the bar
  chart, and the 5 most recent rows with `ORDER BY id DESC LIMIT 5`.
  Returns one dict; also computes `max_dept_count` so the template can size
  the bars as percentages.
- **`roll_no_exists()` / `email_exists()`** — `SELECT 1 … WHERE …`; the
  optional `exclude_id` parameter is what lets *editing* keep your own
  roll number without tripping the UNIQUE check.
- **`add_student(data)`** — one `INSERT` with 9 `?` placeholders.
  `conn.commit()` writes the change to disk permanently; `cur.lastrowid`
  returns the new row's id.
- **`update_student(student_id, data)`** — one `UPDATE … WHERE id = ?`;
  `cur.rowcount` tells us whether a row actually changed.
- **`delete_student(student_id)`** — `DELETE FROM students WHERE id = ?`.

  *Remember: the database does INSERT / UPDATE / DELETE only — "R" (read) is
  the SELECTs above. Together that's CRUD.*

### `validators.py` — friendly form checks

`validate_student(form)` does three things:

1. **Normalises** every field — trims whitespace, upper-cases the roll number,
   lower-cases the email.
2. **Checks** each field and appends a human-readable string to `errors`:
   - name ≥ 2 chars; email matches a regex (roughly `something@something.something`);
     phone only digits/spaces/dashes/`+` (7–15);
   - department must be one of the `DEPARTMENTS` list;
   - semester must convert to an int in 1–8 (`try/except ValueError` catches
     non-numbers);
   - GPA optional, but if given must parse to a float in 0–10;
   - date of birth optional, but must be a real `YYYY-MM-DD` date and not in
     the future (`datetime.strptime` raises `ValueError` on bad dates).
3. **Returns** `(cleaned, errors)` — `cleaned` is a dict of properly *typed*
   values (ints, floats, `None`) ready for the database layer.

The database's UNIQUE/CHECK constraints remain as a second line of defence;
the Python layer exists so the *user* sees a message like
"Roll number 'CS2026001' is already taken" instead of a server error.

### `app.py` — routes (the map of the site)

| Route | Methods | Job |
|---|---|---|
| `/` | GET | dashboard with `get_stats()` |
| `/students` | GET | list + search/filter/sort (all from the query string) |
| `/students/add` | GET, POST | show form / validate → insert |
| `/students/<int:id>` | GET | profile page |
| `/students/<int:id>/edit` | GET, POST | show pre-filled form / validate → update |
| `/students/<int:id>/delete` | POST only | delete |
| `/api/students` | GET | whole table as JSON |

Concepts worth knowing in this file:

- **`@app.route(...)` decorators** bind a URL to a function.
  `<int:student_id>` is a *converter*: the route only matches if the URL part
  is an integer, and it arrives in the function as a Python `int`.
- **GET vs POST.** `methods=["GET", "POST"]` means the same URL serves the
  form (GET) and accepts it (POST). `request.form` holds posted fields;
  `request.args` holds query-string parameters. The list page is GET-only on
  purpose — filters are shareable URLs and never modify data.
- **Post/Redirect/Get.** After a successful POST we
  `return redirect(url_for("students"))` instead of rendering. If the user
  hit *Refresh* on the result, the browser would otherwise re-POST the form
  and (pre-Flask) warn "resubmit your form?" — the redirect avoids it.
- **`flash(message, "success"/"error")`** stashes a one-line message in the
  session cookie; `base.html` displays every pending flash as a coloured
  banner and it's gone on the next request.
- **`render_template(name, **context)`** hands variables to Jinja2.
- **`url_for("route_name", …)`** builds URLs from function names — if a
  route is ever renamed/moved, every link updates automatically.
- **`abort(404)`** + the `@app.errorhandler(404)` function turns "student not
  found" into the friendly 404 page.
- The **API route** just returns `jsonify(get_students())` — the same data
  layer feeding both the human UI and machines.
- `app.run(host="0.0.0.0", port=5000, debug=True)` starts the development
  server. `0.0.0.0` makes it reachable on the local network; `debug=True`
  gives an in-browser traceback page on errors (dev only).

### `templates/` — Jinja2 HTML

- **`base.html`** is the *layout*: `<nav>`, flash-banner loop, `{% block
  content %}`, footer. `request.endpoint` (Flask's internal name for the
  current route) drives the "active" nav underline.
- **Child templates** start with `{% extends "base.html" %}` and fill
  `{% block content %}` (and optionally `{% block title %}`).
- `{{ student.get('roll_no', '') or '' }}` — the *same form template* is
  used for add (empty dict), edit (row dict) and error re-render
  (`request.form`), so nothing the user typed is ever lost after a
  validation error.
- The **sort macro** in `students.html` is a `{% macro %}` that renders each
  header as a link whose `sort_by`/`sort_order` parameters flip the order;
  the current filters are passed along so sorting doesn't wipe the search.
- `{{ "%.2f"|format(s.gpa) }}` is a Jinja **filter** — format a float with
  two decimals.

### `static/css/style.css`

Plain CSS. The `:root { … }` block defines every colour and the shadow as
**CSS variables** — change `--primary` once and buttons, badges, links and
bars all follow. Layout uses **flexbox** (nav, filter bar, page heads) and
**CSS Grid** (stat cards, two-column dashboard, form grid, detail card);
`@media (max-width: …)` collapses everything to one column on phones.

### `seed.py`

A list of 12 realistic sample rows; the script checks
`SELECT COUNT(*)` first and only inserts when the table is empty, so it's
safe to run any number of times.

---

## 🔐 Security notes (asked about in every viva)

1. **SQL injection** — impossible here because every user-supplied value goes
   through `?` placeholders, and the one dynamic piece of SQL (`ORDER BY`)
   is whitelisted. Try typing `1' OR 1=1 --` into the search box: it's treated
   as literal text.
2. **XSS (cross-site scripting)** — Jinja2 **auto-escapes** every `{{ value }}`
   by default, so a name like `<script>alert(1)</script>` displays as text,
   not code.
3. **Form spam / accidental deletes** — destructive actions use POST forms
   plus a `confirm()` dialog, never plain links.
4. **Database-level constraints** — UNIQUE and CHECK rules reject bad data
   even if the Python validation were somehow skipped.
5. **What a production version would add** (out of scope for this project):
   CSRF tokens, a real secret key, user accounts + password hashing
   (e.g. `werkzeug.security`), HTTPS, and a real server (gunicorn) instead of
   Flask's dev server.

---

## 🚀 Ideas to extend it

- Pagination (Flask-SQLAlchemy makes it 3 lines)
- Marks per subject + class averages (new `marks` table with foreign key to `students.id`)
- CSV export button (`csv` module + a `Response` with the right header)
- Login for faculty/admin roles
- Swap SQLite for PostgreSQL — only `database.py` changes
- REST filters on the API: `/api/students?department=…`

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` on port 5000 | close the other app, or change `port=5000` in `app.py` |
| Empty tables on first run | run `python seed.py`, or add students manually |
| "Please reinstall flask" / `ModuleNotFoundError` | activate the venv (`source .venv/bin/activate`) and `pip install -r requirements.txt` |
| I changed code but nothing changed | the dev server auto-reloads on save; if you're running without `debug=True`, restart it |
| Want a clean database | delete `students.db` (app stopped), run `python seed.py` |

---

## 📚 Learning resources

- Flask tutorial (official): https://flask.palletsprojects.com/en/stable/tutorial/
- SQLite tutorial (official): https://www.sqlite.org/tutorial.html
- Jinja2 templates (official): https://jinja.palletsprojects.com/en/stable/templates/
