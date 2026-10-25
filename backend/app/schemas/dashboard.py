from typing import List, Optional
from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class CategoryCount(BaseModel):
    category: str
    sector: str
    count: int


class SectorCount(BaseModel):
    sector: str
    count: int


class TopIssue(BaseModel):
    id: int
    public_id: str
    title: str
    upvotes: int
    status: str


class RecentIssue(BaseModel):
    id: int
    public_id: str
    title: str
    status: str
    created_at: str


class LocationCount(BaseModel):
    location: str
    count: int


class DashboardStats(BaseModel):
    total_issues: int
    by_status: List[StatusCount]
    top_categories: List[CategoryCount]
    by_sector: List[SectorCount]
    most_upvoted: List[TopIssue]
    recent: List[RecentIssue]
    top_locations: List[LocationCount]
    total_users: int
    resolved_last_30_days: int
    avg_resolution_hours: Optional[float] = None
