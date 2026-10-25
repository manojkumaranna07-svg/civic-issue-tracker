from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import Issue, IssueStatus, Upvote, Sector
from ..schemas import MapIssueOut
from .deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/issues", response_model=List[MapIssueOut])
def map_issues(sector_id: Optional[int] = None, status: Optional[IssueStatus] = None,
               db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Only issues with a stored coordinate pair are returned; issues without
    # verified coordinates are intentionally absent from the map.
    q = db.query(Issue).filter(Issue.latitude.isnot(None), Issue.longitude.isnot(None))
    if sector_id:
        q = q.filter(Issue.sector_id == sector_id)
    if status:
        q = q.filter(Issue.status == status)
    issues = q.all()
    out = []
    for i in issues:
        out.append(MapIssueOut(
            id=i.id, public_id=i.public_id, title=i.title, status=i.status,
            sector_name=i.sector.name, latitude=i.latitude, longitude=i.longitude,
            upvote_count=len(i.upvotes)))
    return out
