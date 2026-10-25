from datetime import datetime
from typing import Optional

from fastapi import (APIRouter, Depends, HTTPException, status, UploadFile,
                     File, Form, Query)
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import (Issue, IssueImage, IssueStatusHistory, Upvote, IssueAssignment,
                      Comment, IssueStatus, User, UserRole, Sector, Category, Department)
from ..schemas import (IssueListOut, IssueDetailOut, UpvoteOut, StatusUpdate,
                       AssignmentCreate, CommentCreate, CommentOut)
from ..services import image_service, notification_service, issue_service
from .deps import get_current_user, require_admin, require_admin_or_staff

router = APIRouter(prefix="/api/issues", tags=["issues"])


def _get_issue_or_404(db: Session, issue_id: int) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Issue not found.")
    return issue


@router.post("", response_model=IssueDetailOut, status_code=201)
async def create_issue(
    title: str = Form(..., min_length=4, max_length=200),
    description: str = Form(..., min_length=10, max_length=5000),
    sector_id: int = Form(...),
    category_id: int = Form(...),
    location_text: str = Form(..., min_length=2, max_length=300),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sector = db.get(Sector, sector_id)
    category = db.get(Category, category_id)
    if sector is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector not found.")
    if category is None or category.sector_id != sector.id:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Category does not belong to the selected sector.")
    # Coordinates are only stored as a verified pair picked on the map.
    if (latitude is None) != (longitude is None):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Provide both latitude and longitude, or neither.")
    if latitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Coordinates out of range.")

    issue = Issue(public_id="PENDING", reporter_id=user.id, title=title.strip(),
                  description=description.strip(), sector_id=sector_id,
                  category_id=category_id, location_text=location_text.strip(),
                  latitude=latitude, longitude=longitude, status=IssueStatus.REPORTED)
    db.add(issue)
    db.flush()  # allocate id
    issue.public_id = f"CIV-{issue.created_at.year if issue.created_at else datetime.utcnow().year}-{issue.id:05d}"

    if image is not None and image.filename:
        saved = await image_service.save_issue_image(image, issue.public_id)
        db.add(IssueImage(issue_id=issue.id, **saved))

    db.add(IssueStatusHistory(issue_id=issue.id, old_status=None,
                              new_status=IssueStatus.REPORTED,
                              comment="Issue reported.", changed_by_id=user.id))
    notification_service.notify(
        db, user.id, "submission", f"Issue {issue.public_id} submitted",
        f'Your report "{issue.title}" was received and is awaiting review.', issue.id)
    notification_service.notify_admins(
        db, "submission", f"New issue {issue.public_id}",
        f'{user.name} reported "{issue.title}" in {sector.name} / {category.name}.', issue.id)
    db.commit()
    db.refresh(issue)
    return issue_service.to_issue_detail(db, issue, user.id)


@router.get("", response_model=IssueListOut)
def list_issues(
    q: Optional[str] = None,
    sector_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status_filter: Optional[IssueStatus] = Query(default=None, alias="status"),
    location: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    mine: bool = False,
    assigned_to_me: bool = False,
    sort: str = Query(default="newest", pattern="^(newest|oldest|most_upvoted)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Issue)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Issue.title.ilike(like), Issue.description.ilike(like),
                                 Issue.public_id.ilike(like)))
    if sector_id:
        query = query.filter(Issue.sector_id == sector_id)
    if category_id:
        query = query.filter(Issue.category_id == category_id)
    if status_filter:
        query = query.filter(Issue.status == status_filter)
    if location:
        query = query.filter(Issue.location_text.ilike(f"%{location.strip()}%"))
    if date_from:
        query = query.filter(Issue.created_at >= date_from)
    if date_to:
        query = query.filter(Issue.created_at <= date_to)
    if mine:
        query = query.filter(Issue.reporter_id == user.id)
    if assigned_to_me:
        query = query.join(IssueAssignment, IssueAssignment.issue_id == Issue.id).filter(
            IssueAssignment.assigned_to_id == user.id, IssueAssignment.is_active.is_(True))

    total = query.count()
    if sort == "oldest":
        query = query.order_by(Issue.created_at.asc())
    elif sort == "most_upvoted":
        query = (query.outerjoin(Upvote, Upvote.issue_id == Issue.id)
                 .group_by(Issue.id).order_by(func.count(Upvote.id).desc()))
    else:
        query = query.order_by(Issue.created_at.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return IssueListOut(items=[issue_service.to_issue_out(db, i, user.id) for i in items],
                        total=total, page=page, page_size=page_size)


@router.get("/{issue_id}", response_model=IssueDetailOut)
def get_issue(issue_id: int, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    issue = _get_issue_or_404(db, issue_id)
    return issue_service.to_issue_detail(db, issue, user.id)


@router.delete("/{issue_id}", status_code=204)
def delete_issue(issue_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    issue = _get_issue_or_404(db, issue_id)
    is_admin = user.role == UserRole.ADMIN
    is_own_open = issue.reporter_id == user.id and issue.status == IssueStatus.REPORTED
    if not (is_admin or is_own_open):
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Only an administrator, or the reporter while still 'Reported', can delete an issue.")
    db.delete(issue)
    db.commit()
    return None


@router.post("/{issue_id}/upvote", response_model=UpvoteOut)
def upvote_issue(issue_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    issue = _get_issue_or_404(db, issue_id)
    if db.query(Upvote).filter(Upvote.issue_id == issue.id,
                               Upvote.user_id == user.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "You already supported this issue.")
    db.add(Upvote(issue_id=issue.id, user_id=user.id))
    try:
        db.commit()
    except IntegrityError:  # concurrent duplicate; unique constraint holds
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You already supported this issue.")
    return UpvoteOut(issue_id=issue.id,
                     upvote_count=issue_service.upvote_count(db, issue.id),
                     upvoted_by_me=True)


@router.delete("/{issue_id}/upvote", response_model=UpvoteOut)
def remove_upvote(issue_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    issue = _get_issue_or_404(db, issue_id)
    upvote = db.query(Upvote).filter(Upvote.issue_id == issue.id,
                                     Upvote.user_id == user.id).first()
    if upvote is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "You have not supported this issue.")
    db.delete(upvote)
    db.commit()
    return UpvoteOut(issue_id=issue.id,
                     upvote_count=issue_service.upvote_count(db, issue.id),
                     upvoted_by_me=False)


ALLOWED_NEXT = {
    IssueStatus.REPORTED: {IssueStatus.UNDER_REVIEW, IssueStatus.IN_PROGRESS,
                           IssueStatus.RESOLVED, IssueStatus.REJECTED},
    IssueStatus.UNDER_REVIEW: {IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED,
                               IssueStatus.REJECTED, IssueStatus.REPORTED},
    IssueStatus.IN_PROGRESS: {IssueStatus.RESOLVED, IssueStatus.UNDER_REVIEW},
    IssueStatus.RESOLVED: {IssueStatus.IN_PROGRESS},   # reopen
    IssueStatus.REJECTED: {IssueStatus.UNDER_REVIEW},  # reconsider
}


@router.post("/{issue_id}/status", response_model=IssueDetailOut)
def update_status(issue_id: int, body: StatusUpdate, db: Session = Depends(get_db),
                  user: User = Depends(require_admin_or_staff)):
    issue = _get_issue_or_404(db, issue_id)
    if user.role == UserRole.STAFF:
        assigned = db.query(IssueAssignment).filter(
            IssueAssignment.issue_id == issue.id,
            IssueAssignment.assigned_to_id == user.id,
            IssueAssignment.is_active.is_(True)).first()
        if assigned is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Staff can only update issues assigned to them.")
        if body.status not in (IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED):
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Staff may only set 'In Progress' or 'Resolved'.")
    if body.status == issue.status:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Issue already has this status.")
    if body.status not in ALLOWED_NEXT[issue.status]:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Cannot move from '{issue.status.value}' to '{body.status.value}'.")
    if body.status == IssueStatus.REJECTED and not (body.rejection_reason or body.comment):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "A reason is required when rejecting an issue.")

    old = issue.status
    issue.status = body.status
    if body.status == IssueStatus.REJECTED:
        issue.rejection_reason = body.rejection_reason or body.comment
        issue.resolved_at = None
    elif body.status == IssueStatus.RESOLVED:
        issue.resolved_at = datetime.utcnow()
        issue.rejection_reason = None
    else:
        issue.resolved_at = None
    db.add(IssueStatusHistory(issue_id=issue.id, old_status=old, new_status=body.status,
                              comment=body.comment, changed_by_id=user.id))
    ntype = "resolved" if body.status == IssueStatus.RESOLVED else "status_change"
    notification_service.notify(
        db, issue.reporter_id, ntype,
        f"Issue {issue.public_id}: {body.status.value}",
        f'"{issue.title}" moved from {old.value} to {body.status.value}.'
        + (f" Note: {body.comment}" if body.comment else ""), issue.id)
    db.commit()
    db.refresh(issue)
    return issue_service.to_issue_detail(db, issue, user.id)


@router.post("/{issue_id}/assign", response_model=IssueDetailOut, status_code=201)
def assign_issue(issue_id: int, body: AssignmentCreate, db: Session = Depends(get_db),
                 admin: User = Depends(require_admin)):
    issue = _get_issue_or_404(db, issue_id)
    dept = db.get(Department, body.department_id)
    if dept is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found.")
    staff = None
    if body.assigned_to_id is not None:
        staff = db.get(User, body.assigned_to_id)
        if staff is None or staff.role != UserRole.STAFF:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "assignee must be a department staff user.")
        if staff.department_id != dept.id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "Staff member does not belong to that department.")
    db.query(IssueAssignment).filter(IssueAssignment.issue_id == issue.id,
                                     IssueAssignment.is_active.is_(True)
                                     ).update({"is_active": False})
    db.add(IssueAssignment(issue_id=issue.id, department_id=dept.id,
                           assigned_to_id=staff.id if staff else None,
                           assigned_by_id=admin.id, note=body.note))
    if staff:
        notification_service.notify(
            db, staff.id, "status_change", f"Issue {issue.public_id} assigned to you",
            f'"{issue.title}" was assigned to {dept.name}.', issue.id)
    db.commit()
    db.refresh(issue)
    return issue_service.to_issue_detail(db, issue, admin.id)


@router.post("/{issue_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(issue_id: int, body: CommentCreate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    issue = _get_issue_or_404(db, issue_id)
    is_admin = user.role in (UserRole.ADMIN, UserRole.STAFF)
    comment = Comment(issue_id=issue.id, author_id=user.id,
                      body=body.body.strip(), is_admin=is_admin)
    db.add(comment)
    if is_admin and issue.reporter_id != user.id:
        notification_service.notify(
            db, issue.reporter_id, "comment", f"New official note on {issue.public_id}",
            f'{user.name} commented on "{issue.title}".', issue.id)
    db.commit()
    db.refresh(comment)
    return CommentOut(id=comment.id, author_name=user.name, body=comment.body,
                      is_admin=comment.is_admin, created_at=comment.created_at)
