from sqlalchemy import (Column, Integer, String, DateTime, Text, Boolean,
                        ForeignKey, func)
from sqlalchemy.orm import relationship

from ..database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(40), nullable=False)   # submission, status_change, comment, resolved, announcement
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    user = relationship("User", back_populates="notifications")
    issue = relationship("Issue")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    created_by = relationship("User")
