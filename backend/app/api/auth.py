from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models import User, UserRole
from ..schemas import UserCreate, UserLogin, TokenResponse, UserOut
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")
    user = User(name=body.name.strip(), email=email,
                password_hash=auth_service.hash_password(body.password),
                phone=body.phone, role=UserRole.CITIZEN)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth_service.create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None or not auth_service.verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been deactivated.")
    token = auth_service.create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))
