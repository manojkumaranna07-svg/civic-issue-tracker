from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.issue import IssueStatus


class IssueImageOut(BaseModel):
    id: int
    url: str
    original_name: str
    content_type: str
    size_bytes: int


class StatusHistoryOut(BaseModel):
    id: int
    old_status: Optional[IssueStatus] = None
    new_status: IssueStatus
    comment: Optional[str] = None
    changed_by_name: str
    created_at: datetime


class AssignmentOut(BaseModel):
    id: int
    department_name: str
    assigned_to_name: Optional[str] = None
    assigned_by_name: str
    note: Optional[str] = None
    is_active: bool
    created_at: datetime


class CommentOut(BaseModel):
    id: int
    author_name: str
    body: str
    is_admin: bool
    created_at: datetime


class IssueOut(BaseModel):
    id: int
    public_id: str
    title: str
    description: str
    sector_id: int
    sector_name: str
    category_id: int
    category_name: str
    location_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: IssueStatus
    rejection_reason: Optional[str] = None
    reporter_name: str
    reporter_id: int
    upvote_count: int
    upvoted_by_me: bool = False
    image_count: int = 0
    created_at: datetime
    resolved_at: Optional[datetime] = None


class IssueListOut(BaseModel):
    items: List[IssueOut]
    total: int
    page: int
    page_size: int


class IssueDetailOut(IssueOut):
    images: List[IssueImageOut] = []
    status_history: List[StatusHistoryOut] = []
    comments: List[CommentOut] = []
    assignments: List[AssignmentOut] = []


class MapIssueOut(BaseModel):
    id: int
    public_id: str
    title: str
    status: IssueStatus
    sector_name: str
    latitude: float
    longitude: float
    upvote_count: int


class StatusUpdate(BaseModel):
    status: IssueStatus
    comment: Optional[str] = Field(default=None, max_length=2000)
    rejection_reason: Optional[str] = Field(default=None, max_length=1000)


class AssignmentCreate(BaseModel):
    department_id: int
    assigned_to_id: Optional[int] = None
    note: Optional[str] = Field(default=None, max_length=1000)


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class UpvoteOut(BaseModel):
    issue_id: int
    upvote_count: int
    upvoted_by_me: bool
