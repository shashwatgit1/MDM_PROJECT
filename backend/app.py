"""Student Management System - Flask + SQLite REST API (also serves the frontend)."""
import os, re, sqlite3
from flask import Flask, g, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(BASE, "..", "frontend")
DB_PATH = os.environ.get("SMS_DB", os.path.join(BASE, "students.db"))

app = Flask(__name__, static_folder=None)

SCHEMA = """
CREATE TABLE IF NOT EXISTS classes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no    TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name       TEXT NOT NULL,
    class_id   INTEGER NOT NULL REFERENCES classes(id),
    marks      REAL NOT NULL CHECK (marks BETWEEN 0 AND 100),
    contact    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
"""

SELECT = """SELECT s.id, s.roll_no, s.name, c.name AS class_name, s.marks, s.contact
            FROM students s JOIN classes c ON c.id = s.class_id"""


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ---------- validation ----------
def validate(data, student_id=None):
    """Return (clean, errors). errors is {field: message}."""
    errors, clean = {}, {}
    name = re.sub(r"\s+", " ", str(data.get("name", "")).strip())
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,59}", name):
        errors["name"] = "Enter a name of 2-60 letters."
    clean["name"] = name

    roll = str(data.get("roll_no", "")).strip().upper()
    if not re.fullmatch(r"[A-Z0-9-]{1,20}", roll):
        errors["roll_no"] = "Roll number can use letters, digits and hyphens (max 20)."
    else:
        row = db().execute("SELECT id FROM students WHERE roll_no = ?", (roll,)).fetchone()
        if row and row["id"] != student_id:
            errors["roll_no"] = f"Roll number {roll} is already taken."
    clean["roll_no"] = roll

    cls = re.sub(r"\s+", " ", str(data.get("class_name", "")).strip())
    if not re.fullmatch(r"[A-Za-z0-9 -]{1,20}", cls):
        errors["class_name"] = "Enter a class such as 10-A."
    clean["class_name"] = cls

    try:
        marks = float(data.get("marks"))
        if not 0 <= marks <= 100:
            raise ValueError
        clean["marks"] = round(marks, 2)
    except (TypeError, ValueError):
        errors["marks"] = "Marks must be a number from 0 to 100."

    digits = re.sub(r"[\s-]", "", str(data.get("contact", "")))
    digits = re.sub(r"^(\+91|0)", "", digits)
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        errors["contact"] = "Enter a 10-digit mobile number starting with 6-9."
    clean["contact"] = digits
    return clean, errors


def class_id_for(name):
    conn = db()
    conn.execute("INSERT OR IGNORE INTO classes(name) VALUES (?)", (name,))
    return conn.execute("SELECT id FROM classes WHERE name = ?", (name,)).fetchone()["id"]


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def bad(errors, code=400):
    return jsonify({"error": "Validation failed", "fields": errors}), code


def not_found():
    return jsonify({"error": "Student not found"}), 404


# ---------- API ----------
@app.get("/api/students")
def list_students():
    q = request.args.get("q", "").strip()
    cls = request.args.get("class", "").strip()
    sql, params, where = SELECT, [], []
    if q:
        where.append("(s.name LIKE ? OR s.roll_no LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if cls:
        where.append("c.name = ?")
        params.append(cls)
    if where:
        sql += " WHERE " + " AND ".join(where)
    rows = db().execute(sql + " ORDER BY c.name, s.roll_no", params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/students/<int:sid>")
def get_student(sid):
    row = db().execute(SELECT + " WHERE s.id = ?", (sid,)).fetchone()
    return jsonify(dict(row)) if row else not_found()


@app.post("/api/students")
def add_student():
    data = body()
    if data is None:
        return bad({"_": "Send a JSON object."})
    clean, errors = validate(data)
    if errors:
        return bad(errors, 409 if "already taken" in errors.get("roll_no", "") else 400)
    cur = db().execute(
        "INSERT INTO students(roll_no, name, class_id, marks, contact) VALUES (?,?,?,?,?)",
        (clean["roll_no"], clean["name"], class_id_for(clean["class_name"]), clean["marks"], clean["contact"]))
    db().commit()
    row = db().execute(SELECT + " WHERE s.id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.put("/api/students/<int:sid>")
def update_student(sid):
    if not db().execute("SELECT 1 FROM students WHERE id = ?", (sid,)).fetchone():
        return not_found()
    data = body()
    if data is None:
        return bad({"_": "Send a JSON object."})
    clean, errors = validate(data, student_id=sid)
    if errors:
        return bad(errors, 409 if "already taken" in errors.get("roll_no", "") else 400)
    db().execute(
        "UPDATE students SET roll_no=?, name=?, class_id=?, marks=?, contact=? WHERE id=?",
        (clean["roll_no"], clean["name"], class_id_for(clean["class_name"]), clean["marks"], clean["contact"], sid))
    db().commit()
    return jsonify(dict(db().execute(SELECT + " WHERE s.id = ?", (sid,)).fetchone()))


@app.delete("/api/students/<int:sid>")
def delete_student(sid):
    cur = db().execute("DELETE FROM students WHERE id = ?", (sid,))
    db().commit()
    return ("", 204) if cur.rowcount else not_found()


@app.get("/api/classes")
def list_classes():
    rows = db().execute(
        "SELECT c.name FROM classes c WHERE EXISTS (SELECT 1 FROM students s WHERE s.class_id=c.id) ORDER BY c.name").fetchall()
    return jsonify([r["name"] for r in rows])


@app.get("/api/stats")
def stats():
    r = db().execute("SELECT COUNT(*) n, COALESCE(AVG(marks),0) avg, COALESCE(MAX(marks),0) top FROM students").fetchone()
    by_class = db().execute(
        """SELECT c.name, COUNT(*) n, ROUND(AVG(s.marks),1) avg FROM students s
           JOIN classes c ON c.id=s.class_id GROUP BY c.id ORDER BY c.name""").fetchall()
    topper = db().execute(SELECT + " ORDER BY s.marks DESC LIMIT 1").fetchone()
    return jsonify({"total": r["n"], "average": round(r["avg"], 1), "highest": r["top"],
                    "topper": dict(topper) if topper else None, "by_class": [dict(x) for x in by_class]})


@app.errorhandler(404)
def api_404(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return e


@app.errorhandler(405)
def api_405(e):
    return jsonify({"error": "Method not allowed"}), 405


# ---------- frontend ----------
@app.get("/")
def home():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND, path)


init_db()
if __name__ == "__main__":
    app.run(debug=True, port=5000)
