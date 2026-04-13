from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Prediction, User
from ..schemas import PredictionHistoryItem


router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/me", response_model=List[PredictionHistoryItem])
def get_my_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return predictions
