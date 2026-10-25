import enum
from sqlalchemy import (Column, Integer, String, DateTime, Boolean,
                        Enum, ForeignKey, func)
from sqlalchemy.orm import relationship

from ..database.base import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CITIZEN, index=True)
    phone = Column(String(32), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    # Staff users belong to a department.
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    department = relationship("Department", back_populates="staff_members")
    issues = relationship("Issue", back_populates="reporter")
    upvotes = relationship("Upvote", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    comments = relationship("Comment", back_populates="author")
