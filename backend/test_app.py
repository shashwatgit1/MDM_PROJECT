import os, tempfile, pytest
os.environ["SMS_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
import app as A

@pytest.fixture
def c():
    if os.path.exists(A.DB_PATH): os.remove(A.DB_PATH)
    A.init_db()
    return A.app.test_client()

S = {"name": "Asha Rao", "roll_no": "r1", "class_name": "10-A", "marks": 80, "contact": "9876543210"}

def test_crud_flow(c):
    r = c.post("/api/students", json=S); assert r.status_code == 201
    sid = r.get_json()["id"]; assert r.get_json()["roll_no"] == "R1"
    assert len(c.get("/api/students").get_json()) == 1
    assert c.put(f"/api/students/{sid}", json={**S, "marks": 90}).get_json()["marks"] == 90
    assert c.delete(f"/api/students/{sid}").status_code == 204
    assert c.get(f"/api/students/{sid}").status_code == 404

def test_duplicate_roll(c):
    c.post("/api/students", json=S)
    assert c.post("/api/students", json={**S, "name": "Other Person"}).status_code == 409

def test_invalid_inputs(c):
    for bad in ({"contact": "12345"}, {"marks": 101}, {"marks": "abc"}, {"name": "A1"}, {"roll_no": ""}):
        r = c.post("/api/students", json={**S, **bad}); assert r.status_code == 400
    assert c.post("/api/students", data="nope").status_code == 400

def test_search_edge_cases(c):
    c.post("/api/students", json=S)
    assert len(c.get("/api/students?q=asha").get_json()) == 1
    assert len(c.get("/api/students?q=R1").get_json()) == 1
    assert c.get("/api/students?q=zzz").get_json() == []
    assert c.put("/api/students/999", json=S).status_code == 404
    assert c.delete("/api/students/999").status_code == 404

def test_update_keeps_own_roll(c):
    sid = c.post("/api/students", json=S).get_json()["id"]
    assert c.put(f"/api/students/{sid}", json=S).status_code == 200
