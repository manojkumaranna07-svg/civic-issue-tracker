from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SectorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = None


class SectorOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    sector_id: int
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    sector_id: int
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    sector_id: Optional[int] = None
    contact_email: Optional[str] = Field(default=None, max_length=255)


class DepartmentOut(BaseModel):
    id: int
    name: str
    sector_id: Optional[int] = None
    contact_email: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
