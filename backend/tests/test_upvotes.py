def test_upvote_success(client, admin_h, issue):
    r = client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    assert r.status_code == 200
    body = r.json()
    assert body["upvote_count"] == 1 and body["upvoted_by_me"] is True


def test_duplicate_upvote_rejected(client, admin_h, issue):
    client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    assert r.status_code == 409


def test_remove_upvote(client, admin_h, issue):
    client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    r = client.delete(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    assert r.status_code == 200
    assert r.json()["upvote_count"] == 0 and r.json()["upvoted_by_me"] is False


def test_remove_upvote_without_voting(client, admin_h, issue):
    assert client.delete(f"/api/issues/{issue['id']}/upvote", headers=admin_h).status_code == 404


def test_upvote_count_reflects_multiple_users(client, admin_h, staff_h, issue):
    client.post(f"/api/issues/{issue['id']}/upvote", headers=admin_h)
    r = client.post(f"/api/issues/{issue['id']}/upvote", headers=staff_h)
    assert r.json()["upvote_count"] == 2


def test_upvote_nonexistent_issue(client, admin_h):
    assert client.post("/api/issues/99999/upvote", headers=admin_h).status_code == 404
