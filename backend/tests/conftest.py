"""Test fixtures: isolated temp database and upload dir per test run."""
import io
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="civic-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["UPLOAD_DIR"] = f"{_tmp}/uploads"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["BCRYPT_ROUNDS"] = "4"  # fast hashing in tests only

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app.main import app  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.session import engine, SessionLocal  # noqa: E402
from app.models import (User, UserRole, Sector, Category, Department,  # noqa: E402
                        Issue, IssueStatus)
from app.services import auth_service  # noqa: E402


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db():
    """Clean slate per test, with a minimal catalog and three role users."""
    session = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    sector = Sector(name="Municipal", description="d")
    sector2 = Sector(name="Environment", description="d")
    session.add_all([sector, sector2])
    session.flush()
    cat1 = Category(sector_id=sector.id, name="Potholes")
    cat2 = Category(sector_id=sector.id, name="Garbage")
    cat3 = Category(sector_id=sector2.id, name="Pollution")
    dept = Department(name="Roads Dept", sector_id=sector.id)
    session.add_all([cat1, cat2, cat3, dept])
    session.flush()
    citizen = User(name="Test Citizen", email="citizen@test.example.com",
                   password_hash=auth_service.hash_password("Citizen@123"),
                   role=UserRole.CITIZEN)
    admin = User(name="Test Admin", email="admin@test.example.com",
                 password_hash=auth_service.hash_password("Admin@123"),
                 role=UserRole.ADMIN)
    staff = User(name="Test Staff", email="staff@test.example.com",
                 password_hash=auth_service.hash_password("Staff@123"),
                 role=UserRole.STAFF, department_id=dept.id)
    session.add_all([citizen, admin, staff])
    session.commit()
    session.info["ids"] = {"sector": sector.id, "sector2": sector2.id,
                           "cat1": cat1.id, "cat2": cat2.id, "cat3": cat3.id,
                           "dept": dept.id, "citizen": citizen.id,
                           "admin": admin.id, "staff": staff.id}
    yield session
    session.close()


def _token(client, email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def citizen_h(client, db):
    return _token(client, "citizen@test.example.com", "Citizen@123")


@pytest.fixture()
def admin_h(client, db):
    return _token(client, "admin@test.example.com", "Admin@123")


@pytest.fixture()
def staff_h(client, db):
    return _token(client, "staff@test.example.com", "Staff@123")


def make_png(size=(30, 30), color=(10, 120, 200)):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    buf.seek(0)
    return buf


@pytest.fixture()
def ids(db):
    return db.info["ids"]


@pytest.fixture()
def issue(client, citizen_h, ids):
    r = client.post("/api/issues", data={
        "title": "Broken streetlight on test road",
        "description": "The lamp post near the test junction is dark.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Test Junction"}, headers=citizen_h)
    assert r.status_code == 201, r.text
    return r.json()
