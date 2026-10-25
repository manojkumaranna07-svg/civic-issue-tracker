"""In-app notifications. Interface is deliberately transport-agnostic so
email or push delivery can be added later by extending notify()."""
from sqlalchemy.orm import Session

from ..models import Notification, User, UserRole


def notify(db: Session, user_id: int, type_: str, title: str, message: str,
           issue_id: int | None = None) -> Notification:
    n = Notification(user_id=user_id, type=type_, title=title,
                     message=message, issue_id=issue_id)
    db.add(n)
    return n


def notify_admins(db: Session, type_: str, title: str, message: str,
                  issue_id: int | None = None) -> None:
    admins = db.query(User).filter(User.role == UserRole.ADMIN, User.is_active.is_(True)).all()
    for admin in admins:
        notify(db, admin.id, type_, title, message, issue_id)


def notify_all_users(db: Session, type_: str, title: str, message: str) -> None:
    users = db.query(User).filter(User.is_active.is_(True)).all()
    for u in users:
        notify(db, u.id, type_, title, message, None)
