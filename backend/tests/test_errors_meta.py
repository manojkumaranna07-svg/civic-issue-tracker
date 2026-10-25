def test_openapi_and_swagger_available(client, db):
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_health(client, db):
    assert client.get("/api/health").json()["status"] == "ok"


def test_bootstrap_catalog(client, citizen_h, ids):
    boot = client.get("/api/meta/bootstrap", headers=citizen_h).json()
    assert len(boot["sectors"]) == 2
    assert len(boot["categories"]) == 3
    assert len(boot["departments"]) == 1


def test_admin_manages_catalog(client, admin_h, ids):
    r = client.post("/api/meta/sectors", json={"name": "Transport"}, headers=admin_h)
    assert r.status_code == 201
    assert client.post("/api/meta/sectors", json={"name": "Transport"},
                       headers=admin_h).status_code == 409
    sid = r.json()["id"]
    r = client.post("/api/meta/categories",
                    json={"sector_id": sid, "name": "Bus Stops"}, headers=admin_h)
    assert r.status_code == 201
    assert client.delete(f"/api/meta/categories/{r.json()['id']}",
                         headers=admin_h).status_code == 204
    assert client.delete(f"/api/meta/sectors/{sid}", headers=admin_h).status_code == 204


def test_used_category_cannot_be_deleted(client, admin_h, issue, ids):
    r = client.delete(f"/api/meta/categories/{ids['cat1']}", headers=admin_h)
    assert r.status_code == 409


def test_comments_flow(client, citizen_h, admin_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/comments",
                    json={"body": "I see this daily."}, headers=citizen_h)
    assert r.status_code == 201 and r.json()["is_admin"] is False
    r = client.post(f"/api/issues/{issue['id']}/comments",
                    json={"body": "We are on it."}, headers=admin_h)
    assert r.json()["is_admin"] is True
    detail = client.get(f"/api/issues/{issue['id']}", headers=citizen_h).json()
    assert len(detail["comments"]) == 2


def test_empty_comment_rejected(client, citizen_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/comments", json={"body": ""},
                    headers=citizen_h)
    assert r.status_code == 422
