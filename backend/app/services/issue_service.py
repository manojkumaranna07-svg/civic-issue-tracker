"""Serialization helpers and shared issue queries."""
from sqlalchemy.orm import Session

from ..models import Issue, Upvote
from ..schemas import (IssueOut, IssueDetailOut, IssueImageOut, StatusHistoryOut,
                       AssignmentOut, CommentOut)


def upvote_count(db: Session, issue_id: int) -> int:
    return db.query(Upvote).filter(Upvote.issue_id == issue_id).count()


def has_upvoted(db: Session, issue_id: int, user_id: int | None) -> bool:
    if user_id is None:
        return False
    return db.query(Upvote).filter(Upvote.issue_id == issue_id,
                                   Upvote.user_id == user_id).first() is not None


def to_issue_out(db: Session, issue: Issue, user_id: int | None = None) -> IssueOut:
    return IssueOut(
        id=issue.id, public_id=issue.public_id, title=issue.title,
        description=issue.description,
        sector_id=issue.sector_id, sector_name=issue.sector.name,
        category_id=issue.category_id, category_name=issue.category.name,
        location_text=issue.location_text,
        latitude=issue.latitude, longitude=issue.longitude,
        status=issue.status, rejection_reason=issue.rejection_reason,
        reporter_name=issue.reporter.name, reporter_id=issue.reporter_id,
        upvote_count=upvote_count(db, issue.id),
        upvoted_by_me=has_upvoted(db, issue.id, user_id),
        image_count=len(issue.images),
        created_at=issue.created_at, resolved_at=issue.resolved_at,
    )


def to_issue_detail(db: Session, issue: Issue, user_id: int | None = None) -> IssueDetailOut:
    base = to_issue_out(db, issue, user_id)
    return IssueDetailOut(
        **base.model_dump(),
        images=[IssueImageOut(id=img.id, url=f"/uploads/{img.filename}",
                              original_name=img.original_name,
                              content_type=img.content_type, size_bytes=img.size_bytes)
                for img in issue.images],
        status_history=[StatusHistoryOut(
            id=h.id, old_status=h.old_status, new_status=h.new_status, comment=h.comment,
            changed_by_name=h.changed_by.name, created_at=h.created_at)
            for h in issue.status_history],
        comments=[CommentOut(id=c.id, author_name=c.author.name, body=c.body,
                             is_admin=c.is_admin, created_at=c.created_at)
                  for c in issue.comments],
        assignments=[AssignmentOut(
            id=a.id, department_name=a.department.name,
            assigned_to_name=a.assigned_to.name if a.assigned_to else None,
            assigned_by_name=a.assigned_by.name, note=a.note,
            is_active=a.is_active, created_at=a.created_at)
            for a in issue.assignments],
    )
