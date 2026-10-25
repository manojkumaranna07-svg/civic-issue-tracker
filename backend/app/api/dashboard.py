from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import User
from ..schemas import DashboardStats
from ..services import stats_service
from .deps import require_admin

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return stats_service.dashboard_stats(db)
