def test_admin_full_lifecycle(client, admin_h, citizen_h, issue):
    iid = issue["id"]
    for nxt in ["Under Review", "In Progress", "Resolved"]:
        r = client.post(f"/api/issues/{iid}/status",
                        json={"status": nxt, "comment": f"moving to {nxt}"},
                        headers=admin_h)
        assert r.status_code == 200, r.text
    detail = client.get(f"/api/issues/{iid}", headers=citizen_h).json()
    assert detail["status"] == "Resolved"
    assert detail["resolved_at"] is not None
    transitions = [(h["old_status"], h["new_status"]) for h in detail["status_history"]]
    assert transitions == [(None, "Reported"), ("Reported", "Under Review"),
                           ("Under Review", "In Progress"), ("In Progress", "Resolved")]


def test_reject_requires_reason(client, admin_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Rejected"}, headers=admin_h)
    assert r.status_code == 422


def test_reject_with_reason(client, admin_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Rejected", "rejection_reason": "Duplicate report"},
                    headers=admin_h)
    assert r.status_code == 200
    assert r.json()["rejection_reason"] == "Duplicate report"


def test_illegal_transition_reported_to_resolved_ok_but_skipping_back_blocked(client, admin_h, issue):
    # In Progress -> Reported is not a legal move
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "In Progress"}, headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Reported"}, headers=admin_h)
    assert r.status_code == 422


def test_same_status_rejected(client, admin_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Reported"}, headers=admin_h)
    assert r.status_code == 400


def test_reopen_resolved_issue(client, admin_h, issue):
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "In Progress"}, headers=admin_h)
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "Resolved"}, headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "In Progress", "comment": "reopened"}, headers=admin_h)
    assert r.status_code == 200
    assert r.json()["resolved_at"] is None


def test_staff_updates_assigned_issue(client, admin_h, staff_h, issue, ids):
    client.post(f"/api/issues/{issue['id']}/assign",
                json={"department_id": ids["dept"], "assigned_to_id": ids["staff"]},
                headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "In Progress", "comment": "crew dispatched"},
                    headers=staff_h)
    assert r.status_code == 200


def test_staff_cannot_reject(client, admin_h, staff_h, issue, ids):
    client.post(f"/api/issues/{issue['id']}/assign",
                json={"department_id": ids["dept"], "assigned_to_id": ids["staff"]},
                headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/status",
                    json={"status": "Rejected", "rejection_reason": "x"}, headers=staff_h)
    assert r.status_code == 403


def test_assign_validates_department_and_staff(client, admin_h, issue, ids):
    assert client.post(f"/api/issues/{issue['id']}/assign",
                       json={"department_id": 9999}, headers=admin_h).status_code == 404
    r = client.post(f"/api/issues/{issue['id']}/assign",
                    json={"department_id": ids["dept"], "assigned_to_id": ids["citizen"]},
                    headers=admin_h)
    assert r.status_code == 422


def test_reassignment_supersedes_old(client, admin_h, issue, ids):
    client.post(f"/api/issues/{issue['id']}/assign",
                json={"department_id": ids["dept"]}, headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/assign",
                    json={"department_id": ids["dept"], "assigned_to_id": ids["staff"],
                          "note": "take over"}, headers=admin_h)
    assert r.status_code == 201
    active = [a for a in r.json()["assignments"] if a["is_active"]]
    assert len(active) == 1 and active[0]["assigned_to_name"] == "Test Staff"
