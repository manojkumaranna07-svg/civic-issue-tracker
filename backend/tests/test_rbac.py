def test_citizen_cannot_access_dashboard(client, citizen_h):
    assert client.get("/api/dashboard/stats", headers=citizen_h).status_code == 403


def test_citizen_cannot_list_users(client, citizen_h):
    assert client.get("/api/users", headers=citizen_h).status_code == 403


def test_citizen_cannot_change_status(client, citizen_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Under Review"}, headers=citizen_h)
    assert r.status_code == 403


def test_citizen_cannot_create_sector(client, citizen_h):
    r = client.post("/api/meta/sectors", json={"name": "Hack Sector"}, headers=citizen_h)
    assert r.status_code == 403


def test_citizen_cannot_assign(client, citizen_h, issue, ids):
    r = client.post(f"/api/issues/{issue['id']}/assign",
                    json={"department_id": ids["dept"]}, headers=citizen_h)
    assert r.status_code == 403


def test_citizen_cannot_announce(client, citizen_h):
    r = client.post("/api/announcements", json={"title": "Hi", "body": "x"},
                    headers=citizen_h)
    assert r.status_code == 403


def test_staff_cannot_access_admin_dashboard(client, staff_h):
    assert client.get("/api/dashboard/stats", headers=staff_h).status_code == 403


def test_staff_cannot_update_unassigned_issue(client, staff_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "In Progress"}, headers=staff_h)
    assert r.status_code == 403


def test_unauthenticated_blocked_everywhere(client, db, issue):
    assert client.get("/api/issues").status_code == 401
    assert client.post(f"/api/issues/{issue['id']}/upvote").status_code == 401
    assert client.get("/api/notifications").status_code == 401


def test_admin_can_change_roles(client, admin_h, ids):
    r = client.put(f"/api/users/{ids['citizen']}/role",
                   json={"role": "staff", "department_id": ids["dept"]},
                   headers=admin_h)
    assert r.status_code == 200 and r.json()["role"] == "staff"


def test_admin_cannot_demote_self(client, admin_h, ids):
    r = client.put(f"/api/users/{ids['admin']}/role", json={"role": "citizen"},
                   headers=admin_h)
    assert r.status_code == 400
