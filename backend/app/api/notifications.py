from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import Notification, Announcement, User
from ..schemas import NotificationOut, AnnouncementCreate, AnnouncementOut
from ..services import notification_service
from .deps import get_current_user, require_admin

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/notifications", response_model=List[NotificationOut])
def list_notifications(unread_only: bool = False, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read.is_(False))
    return q.order_by(Notification.created_at.desc()).limit(100).all()


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    n = db.get(Notification, notification_id)
    if n is None or n.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found.")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return n


@router.post("/notifications/read-all", status_code=204)
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == user.id,
                                  Notification.is_read.is_(False)).update({"is_read": True})
    db.commit()
    return None


@router.get("/announcements", response_model=List[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Announcement).filter(Announcement.is_active.is_(True)
                                         ).order_by(Announcement.created_at.desc()).all()
    return [AnnouncementOut(id=a.id, title=a.title, body=a.body,
                            created_by_name=a.created_by.name,
                            is_active=a.is_active, created_at=a.created_at) for a in rows]


@router.post("/announcements", response_model=AnnouncementOut, status_code=201)
def create_announcement(body: AnnouncementCreate, db: Session = Depends(get_db),
                        admin: User = Depends(require_admin)):
    a = Announcement(title=body.title.strip(), body=body.body.strip(),
                     created_by_id=admin.id)
    db.add(a)
    db.flush()
    notification_service.notify_all_users(db, "announcement", a.title, a.body[:300])
    db.commit()
    db.refresh(a)
    return AnnouncementOut(id=a.id, title=a.title, body=a.body,
                           created_by_name=admin.name, is_active=a.is_active,
                           created_at=a.created_at)
