"""Safe image upload handling: type sniffing, size limits, generated filenames."""
import io
import uuid
from pathlib import Path

from PIL import Image
from fastapi import HTTPException, UploadFile

from ..config import settings

# Real signatures we accept; the extension on the stored file follows the
# detected image format, never the user-supplied filename.
FORMAT_EXT = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "GIF": ".gif"}


async def save_issue_image(upload: UploadFile, issue_public_id: str) -> dict:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded image is empty.")
    if len(data) > settings.MAX_UPLOAD_BYTES:
        mb = settings.MAX_UPLOAD_BYTES // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"Image exceeds the {mb} MB size limit.")
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
    except Exception:
        raise HTTPException(status_code=422, detail="File is not a valid image.")
    ext = FORMAT_EXT.get(img.format)
    if ext is None:
        raise HTTPException(status_code=415,
                            detail="Unsupported image type. Use JPEG, PNG, WEBP or GIF.")
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{issue_public_id.lower()}-{uuid.uuid4().hex[:12]}{ext}"
    path = settings.UPLOAD_DIR / filename
    path.write_bytes(data)
    return {
        "filename": filename,
        "original_name": Path(upload.filename or "image").name[:200],
        "content_type": Image.MIME.get(img.format, "application/octet-stream"),
        "size_bytes": len(data),
    }
