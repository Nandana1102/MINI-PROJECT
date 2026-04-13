from __future__ import annotations

from collections import Counter
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from ..models import Prediction, User
from ..schemas import AdminDashboardStats, PredictionHistoryItem, UserRead


router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminDashboardStats)
def get_admin_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).all()

    risk_counter = Counter(prediction.predicted_risk for prediction in predictions)

    return AdminDashboardStats(
        total_users=len(users),
        total_admins=sum(1 for user in users if (user.role or "user").lower() == "admin"),
        total_predictions=len(predictions),
        risk_distribution={
            "Low": risk_counter.get("Low", 0),
            "Moderate": risk_counter.get("Moderate", 0),
            "High": risk_counter.get("High", 0),
        },
        recent_users=users[:5],
        recent_predictions=predictions[:5],
    )


@router.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/predictions", response_model=List[PredictionHistoryItem])
def get_all_predictions(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return db.query(Prediction).order_by(Prediction.created_at.desc()).all()
