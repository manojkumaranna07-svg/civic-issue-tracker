def test_register_success(client, db):
    r = client.post("/api/auth/register", json={
        "name": "Fresh User", "email": "fresh@test.example.com",
        "password": "Password1!"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["role"] == "citizen"
    assert body["access_token"]
    assert "password" not in str(body["user"]).lower()


def test_register_duplicate_email(client, citizen_h):
    r = client.post("/api/auth/register", json={
        "name": "Copy Cat", "email": "citizen@test.example.com",
        "password": "Password1!"})
    assert r.status_code == 409


def test_register_invalid_email(client, db):
    r = client.post("/api/auth/register", json={
        "name": "Bad Mail", "email": "not-an-email", "password": "Password1!"})
    assert r.status_code == 422


def test_register_short_password(client, db):
    r = client.post("/api/auth/register", json={
        "name": "Weak Pass", "email": "weak@test.example.com", "password": "abc"})
    assert r.status_code == 422


def test_login_success(client, db):
    r = client.post("/api/auth/login", json={
        "email": "citizen@test.example.com", "password": "Citizen@123"})
    assert r.status_code == 200
    assert r.json()["user"]["email"] == "citizen@test.example.com"


def test_login_wrong_password(client, db):
    r = client.post("/api/auth/login", json={
        "email": "citizen@test.example.com", "password": "WrongPass1"})
    assert r.status_code == 401


def test_login_unknown_email(client, db):
    r = client.post("/api/auth/login", json={
        "email": "ghost@test.example.com", "password": "Password1!"})
    assert r.status_code == 401


def test_protected_route_requires_token(client, db):
    assert client.get("/api/users/me").status_code == 401


def test_malformed_token(client, db):
    r = client.get("/api/users/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


def test_profile_update(client, citizen_h):
    r = client.put("/api/users/me", json={"name": "Renamed Citizen", "phone": "9000000001"},
                   headers=citizen_h)
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed Citizen"
    me = client.get("/api/users/me", headers=citizen_h).json()
    assert me["phone"] == "9000000001"


def test_password_change(client, citizen_h):
    r = client.put("/api/users/me/password", json={
        "current_password": "Citizen@123", "new_password": "NewPass@123"}, headers=citizen_h)
    assert r.status_code == 204
    assert client.post("/api/auth/login", json={
        "email": "citizen@test.example.com", "password": "NewPass@123"}).status_code == 200


def test_password_change_wrong_current(client, citizen_h):
    r = client.put("/api/users/me/password", json={
        "current_password": "nope", "new_password": "NewPass@123"}, headers=citizen_h)
    assert r.status_code == 400


def test_deactivated_user_token_rejected(client, citizen_h, db):
    from app.models import User
    u = db.query(User).filter(User.email == "citizen@test.example.com").one()
    u.is_active = False
    db.commit()
    assert client.get("/api/users/me", headers=citizen_h).status_code == 401
