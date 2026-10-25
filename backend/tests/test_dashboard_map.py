def test_dashboard_counts(client, admin_h, citizen_h, issue, ids):
    stats = client.get("/api/dashboard/stats", headers=admin_h).json()
    assert stats["total_issues"] == 1
    by = {s["status"]: s["count"] for s in stats["by_status"]}
    assert by["Reported"] == 1 and by["Resolved"] == 0
    assert stats["total_users"] >= 3
    assert stats["top_categories"][0]["category"] == "Potholes"


def test_dashboard_avg_resolution(client, admin_h, issue):
    client.post(f"/api/issues/{issue['id']}/status",
                json={"status": "Resolved"}, headers=admin_h)
    stats = client.get("/api/dashboard/stats", headers=admin_h).json()
    by = {s["status"]: s["count"] for s in stats["by_status"]}
    assert by["Resolved"] == 1
    assert stats["avg_resolution_hours"] is not None


def test_map_excludes_uncoordinated_issues(client, citizen_h, issue):
    assert client.get("/api/map/issues", headers=citizen_h).json() == []


def test_map_includes_coordinated_issues_only(client, citizen_h, issue, ids):
    client.post("/api/issues", data={
        "title": "Mapped one", "description": "Has real coordinates.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Beach", "latitude": 13.05, "longitude": 80.28},
        headers=citizen_h)
    m = client.get("/api/map/issues", headers=citizen_h).json()
    assert len(m) == 1 and m[0]["title"] == "Mapped one"


def test_map_status_filter(client, citizen_h, admin_h, ids):
    r = client.post("/api/issues", data={
        "title": "Mapped two", "description": "Has coordinates too.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Beach", "latitude": 13.05, "longitude": 80.28},
        headers=citizen_h).json()
    assert client.get("/api/map/issues?status=Resolved", headers=citizen_h).json() == []
    client.post(f"/api/issues/{r['id']}/status",
                json={"status": "Resolved"}, headers=admin_h)
    assert len(client.get("/api/map/issues?status=Resolved",
                          headers=citizen_h).json()) == 1
