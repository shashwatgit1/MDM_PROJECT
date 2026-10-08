"""Optional: load sample students.  Run: python seed.py"""
import app
rows = [("Aarav Deshmukh","10-A","101",88.5,"9822012345"),("Isha Kulkarni","10-A","102",92,"9823098765"),
        ("Rohan Patil","10-B","201",67.25,"9970011223"),("Sneha Joshi","9-A","301",74,"8087654321"),
        ("Kabir Sharma","9-A","302",45.5,"7020304050"),("Meera Nair","10-B","202",81,"9011223344")]
with app.app.app_context():
    d = app.db()
    for name, cls, roll, marks, contact in rows:
        if not d.execute("SELECT 1 FROM students WHERE roll_no=?", (roll,)).fetchone():
            d.execute("INSERT INTO students(roll_no,name,class_id,marks,contact) VALUES (?,?,?,?,?)",
                      (roll, name, app.class_id_for(cls), marks, contact))
    d.commit()
print("Seeded.")
