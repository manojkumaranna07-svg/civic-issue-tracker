import io
from .conftest import make_png


def _post(client, headers, ids, files):
    return client.post("/api/issues", data={
        "title": "Upload test", "description": "Checking image validation.",
        "sector_id": ids["sector"], "category_id": ids["cat1"],
        "location_text": "Upload Lane"}, files=files, headers=headers)


def test_valid_png_upload(client, citizen_h, ids):
    r = _post(client, citizen_h, ids, {"image": ("shot.png", make_png(), "image/png")})
    assert r.status_code == 201, r.text
    img = r.json()["images"][0]
    assert img["url"].startswith("/uploads/")
    assert img["original_name"] == "shot.png"
    # stored under a generated safe name, not the user-supplied one
    assert "shot.png" not in img["url"]


def test_uploaded_file_is_served(client, citizen_h, ids):
    r = _post(client, citizen_h, ids, {"image": ("shot.png", make_png(), "image/png")})
    url = r.json()["images"][0]["url"]
    assert client.get(url).status_code == 200


def test_non_image_rejected(client, citizen_h, ids):
    r = _post(client, citizen_h, ids,
              {"image": ("evil.png", io.BytesIO(b"this is not an image"), "image/png")})
    assert r.status_code == 422


def test_executable_disguised_as_image_rejected(client, citizen_h, ids):
    r = _post(client, citizen_h, ids,
              {"image": ("runme.png", io.BytesIO(b"MZ\x90\x00\x03" + b"\x00" * 100),
                         "image/png")})
    assert r.status_code == 422


def test_svg_rejected_as_unsupported(client, citizen_h, ids):
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    r = _post(client, citizen_h, ids, {"image": ("x.svg", io.BytesIO(svg), "image/svg+xml")})
    assert r.status_code in (415, 422)


def test_oversize_image_rejected(client, citizen_h, ids, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_BYTES", 50)
    big = make_png(size=(80, 80))  # any real PNG exceeds 50 bytes
    r = _post(client, citizen_h, ids, {"image": ("big.png", big, "image/png")})
    assert r.status_code == 413


def test_jpeg_accepted(client, citizen_h, ids):
    buf = io.BytesIO()
    from PIL import Image
    Image.new("RGB", (20, 20), (250, 0, 0)).save(buf, "JPEG")
    buf.seek(0)
    r = _post(client, citizen_h, ids, {"image": ("photo.jpg", buf, "image/jpeg")})
    assert r.status_code == 201
    assert r.json()["images"][0]["url"].endswith(".jpg")
