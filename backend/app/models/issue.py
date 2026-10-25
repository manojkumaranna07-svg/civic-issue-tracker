import enum
from sqlalchemy import (Column, Integer, String, DateTime, Text, Float, Boolean,
                        Enum, ForeignKey, UniqueConstraint, Index, func)
from sqlalchemy.orm import relationship

from ..database.base import Base


class IssueStatus(str, enum.Enum):
    REPORTED = "Reported"
    UNDER_REVIEW = "Under Review"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    REJECTED = "Rejected"


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        Index("ix_issues_status_created", "status", "created_at"),
        Index("ix_issues_sector_category", "sector_id", "category_id"),
    )

    id = Column(Integer, primary_key=True)
    public_id = Column(String(20), nullable=False, unique=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    location_text = Column(String(300), nullable=False)
    # NULL when the reporter did not supply verified coordinates; such issues
    # are shown in lists only, never as a misleading map marker.
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(IssueStatus), nullable=False, default=IssueStatus.REPORTED, index=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    reporter = relationship("User", back_populates="issues")
    sector = relationship("Sector", back_populates="issues")
    category = relationship("Category", back_populates="issues")
    images = relationship("IssueImage", back_populates="issue", cascade="all, delete-orphan")
    status_history = relationship("IssueStatusHistory", back_populates="issue",
                                  cascade="all, delete-orphan", order_by="IssueStatusHistory.created_at")
    upvotes = relationship("Upvote", back_populates="issue", cascade="all, delete-orphan")
    assignments = relationship("IssueAssignment", back_populates="issue", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan",
                            order_by="Comment.created_at")


class IssueImage(Base):
    __tablename__ = "issue_images"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)          # safe generated name on disk
    original_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    issue = relationship("Issue", back_populates="images")


class IssueStatusHistory(Base):
    __tablename__ = "issue_status_history"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    old_status = Column(Enum(IssueStatus), nullable=True)   # NULL for the initial entry
    new_status = Column(Enum(IssueStatus), nullable=False)
    comment = Column(Text, nullable=True)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    issue = relationship("Issue", back_populates="status_history")
    changed_by = relationship("User")


class Upvote(Base):
    __tablename__ = "upvotes"
    __table_args__ = (UniqueConstraint("issue_id", "user_id", name="uq_upvote_issue_user"),)

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    issue = relationship("Issue", back_populates="upvotes")
    user = relationship("User", back_populates="upvotes")


class IssueAssignment(Base):
    __tablename__ = "issue_assignments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # staff user
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    issue = relationship("Issue", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")
