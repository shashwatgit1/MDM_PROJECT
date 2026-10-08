# Roll Call - Student Management System
Flask + SQLite backend, vanilla HTML/CSS/JS frontend (Node/Vite tooling optional).

## Run (simplest - Flask serves everything)
    cd backend
    pip install -r requirements.txt
    python seed.py        # optional sample data
    python app.py         # open http://127.0.0.1:5000

## Run with Node tooling (hot reload)
    cd backend && python app.py      # terminal 1
    cd frontend && npm install && npm run dev   # terminal 2 -> http://localhost:5173

## Tests
    cd backend && python -m pytest -q

## API
| Method | Path | Purpose |
|---|---|---|
| GET | /api/students?q=&class= | List / search by name or roll no |
| GET | /api/students/<id> | One student |
| POST | /api/students | Add (409 on duplicate roll no) |
| PUT | /api/students/<id> | Update |
| DELETE | /api/students/<id> | Delete |
| GET | /api/classes, /api/stats | Filters and dashboard data |

## Schema
`classes(id, name UNIQUE)` 1-to-many `students(id, roll_no UNIQUE, name, class_id FK, marks 0-100, contact, created_at)`
