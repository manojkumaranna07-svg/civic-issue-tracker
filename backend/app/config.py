"""Application configuration. Secrets come from environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]      # backend/
PROJECT_ROOT = BASE_DIR.parent                       # civic-issue-tracker/


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    TOKEN_EXPIRE_HOURS: int = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/civic.db")
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    FRONTEND_DIST: Path = PROJECT_ROOT / "frontend" / "dist"


settings = Settings()
