from .conftest import make_png


def test_create_issue_success(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Water leak near park", "description": "Pipe burst flooding the lane.",
        "sector_id": ids["sector"], "category_id": ids["cat2"],
        "location_text": "Park Lane"}, headers=citizen_h)
    assert r.status_code == 201
    body = r.json()
    assert body["public_id"].startswith("CIV-")
    assert body["status"] == "Reported"
    assert body["latitude"] is None and body["longitude"] is None
    assert len(body["status_history"]) == 1


def test_create_issue_with_coordinates(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Mapped issue", "description": "Coordinates supplied via map pick.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Map Point", "latitude": 13.0827, "longitude": 80.2707},
        headers=citizen_h)
    assert r.status_code == 201
    assert r.json()["latitude"] == 13.0827


def test_create_issue_half_coordinates_rejected(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Half mapped", "description": "Only latitude supplied.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Map Point", "latitude": 13.0827}, headers=citizen_h)
    assert r.status_code == 422


def test_create_issue_out_of_range_coordinates(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Bad coords", "description": "Latitude beyond valid range.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Nowhere", "latitude": 123.0, "longitude": 10.0},
        headers=citizen_h)
    assert r.status_code == 422


def test_create_issue_category_sector_mismatch(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Wrong pairing", "description": "Category from another sector.",
        "sector_id": ids["sector2"], "category_id": ids["cat1"],
        "location_text": "Somewhere"}, headers=citizen_h)
    assert r.status_code == 422


def test_create_issue_missing_fields(client, citizen_h):
    r = client.post("/api/issues", data={"title": "Only title"}, headers=citizen_h)
    assert r.status_code == 422


def test_create_issue_requires_auth(client, ids):
    r = client.post("/api/issues", data={
        "title": "No auth", "description": "should fail",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "x"})
    assert r.status_code == 401


def test_list_pagination(client, citizen_h, ids):
    for n in range(5):
        client.post("/api/issues", data={
            "title": f"Bulk issue {n}", "description": f"Bulk description {n}.",
            "sector_id": ids["sector"], "category_id": ids["cat1"],
            "location_text": "Bulk"}, headers=citizen_h)
    r = client.get("/api/issues?page=1&page_size=3", headers=citizen_h).json()
    assert r["total"] == 5 and len(r["items"]) == 3
    r2 = client.get("/api/issues?page=2&page_size=3", headers=citizen_h).json()
    assert len(r2["items"]) == 2


def test_search_by_title(client, citizen_h, issue):
    r = client.get("/api/issues?q=streetlight", headers=citizen_h).json()
    assert r["total"] == 1 and r["items"][0]["id"] == issue["id"]


def test_search_no_match(client, citizen_h, issue):
    assert client.get("/api/issues?q=zzzznothing", headers=citizen_h).json()["total"] == 0


def test_filter_by_sector_and_status(client, citizen_h, admin_h, issue, ids):
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "Under Review"}, headers=admin_h)
    r = client.get(f"/api/issues?sector_id={ids['sector']}&status=Under Review",
                   headers=citizen_h).json()
    assert r["total"] == 1
    r = client.get(f"/api/issues?status=Resolved", headers=citizen_h).json()
    assert r["total"] == 0


def test_filter_by_location(client, citizen_h, issue):
    r = client.get("/api/issues?location=junction", headers=citizen_h).json()
    assert r["total"] == 1


def test_mine_filter(client, citizen_h, admin_h, issue):
    assert client.get("/api/issues?mine=1", headers=citizen_h).json()["total"] == 1
    assert client.get("/api/issues?mine=1", headers=admin_h).json()["total"] == 0


def test_sort_most_upvoted(client, citizen_h, admin_h, staff_h, issue, ids):
    other = client.post("/api/issues", data={
        "title": "Second issue", "description": "Another one here.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Elsewhere"}, headers=citizen_h).json()
    client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    client.post(f"/api/issues/{issue['id']}/upvote", headers=staff_h)
    client.post(f"/api/issues/{other['id']}/upvote", headers=admin_h)
    items = client.get("/api/issues?sort=most_upvoted", headers=citizen_h).json()["items"]
    assert items[0]["id"] == issue["id"]


def test_issue_detail(client, citizen_h, issue):
    r = client.get(f"/api/issues/{issue['id']}", headers=citizen_h)
    assert r.status_code == 200
    assert r.json()["public_id"] == issue["public_id"]


def test_issue_detail_404(client, citizen_h):
    assert client.get("/api/issues/99999", headers=citizen_h).status_code == 404


def test_reporter_can_delete_own_reported_issue(client, citizen_h, issue):
    assert client.delete(f"/api/issues/{issue['id']}", headers=citizen_h).status_code == 204
    assert client.get(f"/api/issues/{issue['id']}", headers=citizen_h).status_code == 404


def test_reporter_cannot_delete_reviewed_issue(client, citizen_h, admin_h, issue):
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "Under Review"}, headers=admin_h)
    assert client.delete(f"/api/issues/{issue['id']}", headers=citizen_h).status_code == 403


def test_cannot_delete_others_issue(client, citizen_h, issue):
    # register a second citizen and try to delete
    client.post("/api/auth/register", json={
        "name": "Other User", "email": "other@test.example.com", "password": "Password1!"})
    other = client.post("/api/auth/login", json={
        "email": "other@test.example.com", "password": "Password1!"}).json()["access_token"]
    r = client.delete(f"/api/issues/{issue['id']}",
                      headers={"Authorization": f"Bearer {other}"})
    assert r.status_code == 403
