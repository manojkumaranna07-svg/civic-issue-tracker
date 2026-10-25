def test_submission_notifies_reporter(client, citizen_h, issue):
    notes = client.get("/api/notifications", headers=citizen_h).json()
    assert any(n["type"] == "submission" for n in notes)


def test_status_change_notifies_reporter(client, admin_h, citizen_h, issue):
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "Under Review", "comment": "seen"}, headers=admin_h)
    notes = client.get("/api/notifications", headers=citizen_h).json()
    assert any(n["type"] == "status_change" and "Under Review" in n["message"]
               for n in notes)


def test_admin_comment_notifies_reporter(client, admin_h, citizen_h, issue):
    client.post(f"/api/issues/{issue['id']}/comments",
                json={"body": "Official note here."}, headers=admin_h)
    notes = client.get("/api/notifications", headers=citizen_h).json()
    assert any(n["type"] == "comment" for n in notes)


def test_mark_read_and_unread_filter(client, citizen_h, issue):
    notes = client.get("/api/notifications?unread_only=1", headers=citizen_h).json()
    assert notes
    nid = notes[0]["id"]
    r = client.post(f"/api/notifications/{nid}/read", headers=citizen_h)
    assert r.json()["is_read"] is True
    remaining = client.get("/api/notifications?unread_only=1", headers=citizen_h).json()
    assert all(n["id"] != nid for n in remaining)


def test_read_all(client, citizen_h, issue):
    assert client.post("/api/notifications/read-all", headers=citizen_h).status_code == 204
    assert client.get("/api/notifications?unread_only=1", headers=citizen_h).json() == []


def test_cannot_read_others_notification(client, admin_h, citizen_h, issue):
    notes = client.get("/api/notifications", headers=citizen_h).json()
    assert client.post(f"/api/notifications/{notes[0]['id']}/read",
                       headers=admin_h).status_code == 404


def test_announcement_reaches_all_users(client, admin_h, citizen_h):
    client.post("/api/announcements",
                json={"title": "Camp notice", "body": "Grievance camp Saturday."},
                headers=admin_h)
    notes = client.get("/api/notifications", headers=citizen_h).json()
    assert any(n["type"] == "announcement" and n["title"] == "Camp notice" for n in notes)
    anns = client.get("/api/announcements", headers=citizen_h).json()
    assert any(a["title"] == "Camp notice" for a in anns)


def test_assignment_notifies_staff(client, admin_h, staff_h, issue, ids):
    client.post(f"/api/issues/{issue['id']}/assign",
                json={"department_id": ids["dept"], "assigned_to_id": ids["staff"]},
                headers=admin_h)
    notes = client.get("/api/notifications", headers=staff_h).json()
    assert any("assigned to you" in n["title"] for n in notes)
