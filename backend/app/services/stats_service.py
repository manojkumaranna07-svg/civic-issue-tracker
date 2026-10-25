"""Dashboard statistics. Every number is computed live from the database;
nothing is fabricated. Definitions:
- by_status: count of issues grouped by current status.
- avg_resolution_hours: mean of (resolved_at - created_at) over resolved issues.
- top_locations: exact location_text strings, case-insensitively grouped.
"""
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Issue, IssueStatus, User, Sector, Category, Upvote


def dashboard_stats(db: Session) -> dict:
    by_status_rows = (db.query(Issue.status, func.count(Issue.id))
                      .group_by(Issue.status).all())
    status_map = {s.value: 0 for s in IssueStatus}
    for status, count in by_status_rows:
        status_map[status.value] = count

    top_cats = (db.query(Category.name, Sector.name, func.count(Issue.id))
                .join(Issue, Issue.category_id == Category.id)
                .join(Sector, Sector.id == Issue.sector_id)
                .group_by(Category.id).order_by(func.count(Issue.id).desc())
                .limit(8).all())

    by_sector = (db.query(Sector.name, func.count(Issue.id))
                 .join(Issue, Issue.sector_id == Sector.id)
                 .group_by(Sector.id).order_by(func.count(Issue.id).desc()).all())

    most_upvoted = (db.query(Issue, func.count(Upvote.id).label("n"))
                    .join(Upvote, Upvote.issue_id == Issue.id)
                    .group_by(Issue.id).order_by(func.count(Upvote.id).desc())
                    .limit(5).all())

    recent = db.query(Issue).order_by(Issue.created_at.desc()).limit(6).all()

    top_locations = (db.query(func.lower(Issue.location_text), func.count(Issue.id))
                     .group_by(func.lower(Issue.location_text))
                     .order_by(func.count(Issue.id).desc()).limit(8).all())

    resolved_rows = db.query(Issue.created_at, Issue.resolved_at).filter(
        Issue.status == IssueStatus.RESOLVED, Issue.resolved_at.isnot(None)).all()
    hours = [(r.created_at and r.resolved_at) and (r.resolved_at - r.created_at).total_seconds() / 3600
             for r in resolved_rows]
    hours = [h for h in hours if h is not None]
    avg_hours = round(sum(hours) / len(hours), 1) if hours else None

    cutoff = datetime.utcnow() - timedelta(days=30)
    resolved_30 = db.query(Issue).filter(Issue.status == IssueStatus.RESOLVED,
                                         Issue.resolved_at >= cutoff).count()

    return {
        "total_issues": db.query(Issue).count(),
        "by_status": [{"status": k, "count": v} for k, v in status_map.items()],
        "top_categories": [{"category": c, "sector": s, "count": n} for c, s, n in top_cats],
        "by_sector": [{"sector": s, "count": n} for s, n in by_sector],
        "most_upvoted": [{"id": i.id, "public_id": i.public_id, "title": i.title,
                          "upvotes": n, "status": i.status.value} for i, n in most_upvoted],
        "recent": [{"id": i.id, "public_id": i.public_id, "title": i.title,
                    "status": i.status.value, "created_at": i.created_at.isoformat()} for i in recent],
        "top_locations": [{"location": loc, "count": n} for loc, n in top_locations],
        "total_users": db.query(User).count(),
        "resolved_last_30_days": resolved_30,
        "avg_resolution_hours": avg_hours,
    }
