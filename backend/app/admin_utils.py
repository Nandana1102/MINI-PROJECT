from __future__ import annotations

from sqlalchemy.orm import Session

from .models import User


def is_admin(user: User) -> bool:
    return (user.role or "user").lower() == "admin"


def count_admins(db: Session) -> int:
    return db.query(User).filter(User.role == "admin").count()
