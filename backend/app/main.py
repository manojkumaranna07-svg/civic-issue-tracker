from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database.base import Base
from .database.session import engine
from . import models  # noqa: F401 - register tables
from .api import auth, users, meta, issues, map_data, notifications, dashboard

app = FastAPI(
    title="Civic Issue Tracker API",
    description="Report, track and resolve community issues. Interactive docs at /docs.",
    version="1.0.0",
)

# The production frontend is served by this app; CORS only matters for the
# Vite dev server on localhost:5173.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meta.router)
app.include_router(issues.router)
app.include_router(map_data.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "app": "civic-issue-tracker"}


settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

if settings.FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(settings.FRONTEND_DIST / "assets")),
              name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        """Serve the built React app; unknown paths fall back to index.html."""
        candidate = settings.FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(settings.FRONTEND_DIST / "index.html"))
