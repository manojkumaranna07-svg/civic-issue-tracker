from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    issue_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=3, max_length=4000)


class AnnouncementOut(BaseModel):
    id: int
    title: str
    body: str
    created_by_name: str
    is_active: bool
    created_at: datetime
