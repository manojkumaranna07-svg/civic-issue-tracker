from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import User, UserRole, Department
from ..schemas import UserOut, UserUpdate, PasswordChange, AdminRoleUpdate
from ..services import auth_service
from .deps import get_current_user, require_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
def update_me(body: UserUpdate, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    if body.name is not None:
        user.name = body.name.strip()
    if body.phone is not None:
        user.phone = body.phone or None
    db.commit()
    db.refresh(user)
    return user


@router.put("/me/password", status_code=204)
def change_password(body: PasswordChange, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    if not auth_service.verify_password(body.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect.")
    user.password_hash = auth_service.hash_password(body.new_password)
    db.commit()
    return None


@router.get("", response_model=List[UserOut])
def list_users(role: Optional[UserRole] = None, db: Session = Depends(get_db),
               admin: User = Depends(require_admin)):
    q = db.query(User)
    if role is not None:
        q = q.filter(User.role == role)
    return q.order_by(User.created_at.desc()).all()


@router.put("/{user_id}/role", response_model=UserOut)
def update_user_role(user_id: int, body: AdminRoleUpdate, db: Session = Depends(get_db),
                     admin: User = Depends(require_admin)):
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if target.id == admin.id and body.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "You cannot remove your own administrator role.")
    if body.role == UserRole.STAFF:
        if body.department_id is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "Staff users must belong to a department.")
        if db.get(Department, body.department_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found.")
        target.department_id = body.department_id
    else:
        target.department_id = None
    target.role = body.role
    if body.is_active is not None:
        if target.id == admin.id and not body.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "You cannot deactivate your own account.")
        target.is_active = body.is_active
    db.commit()
    db.refresh(target)
    return target
