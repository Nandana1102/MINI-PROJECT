from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import Token, UserCreate, UserLanguagePreferenceUpdate, UserLogin, UserRead
from ..security import create_access_token, get_password_hash, verify_password


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_input: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.email == user_input.email) | (User.username == user_input.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    user = User(
        username=user_input.username,
        email=user_input.email,
        hashed_password=get_password_hash(user_input.password),
        role="user",
        preferred_language=user_input.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_input: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_input.email).first()
    if not user or not verify_password(user_input.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=user.email)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/preferences/language", response_model=UserRead)
def update_language_preference(
    payload: UserLanguagePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.preferred_language = payload.preferred_language
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
