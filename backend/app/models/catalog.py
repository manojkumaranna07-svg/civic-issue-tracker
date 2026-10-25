from sqlalchemy import (Column, Integer, String, DateTime, Text,
                        ForeignKey, UniqueConstraint, func)
from sqlalchemy.orm import relationship

from ..database.base import Base


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    categories = relationship("Category", back_populates="sector", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="sector")
    issues = relationship("Issue", back_populates="sector")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("sector_id", "name", name="uq_category_sector_name"),)

    id = Column(Integer, primary_key=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    sector = relationship("Sector", back_populates="categories")
    issues = relationship("Issue", back_populates="category")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False, unique=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True, index=True)
    contact_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    sector = relationship("Sector", back_populates="departments")
    staff_members = relationship("User", back_populates="department")
    assignments = relationship("IssueAssignment", back_populates="department")
