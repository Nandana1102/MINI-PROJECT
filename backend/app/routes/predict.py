from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Prediction, User
from ..schemas import PredictionRequest, PredictionResponse
from ..services.ml_service import run_prediction


router = APIRouter(prefix="/api", tags=["Prediction"])


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "FastAPI backend is running"}


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = run_prediction(payload.model_dump())

    prediction = Prediction(
        user_id=current_user.id,
        model_name=result["model_name"],
        diet_score=result["user_data"]["diet_score"],
        sleep_hours=result["user_data"]["sleep_hours"],
        activity_level=result["user_data"]["activity_level"],
        bmi=result["user_data"]["bmi"],
        bmi_category=result["user_data"]["bmi_category"],
        hrs_score=result["user_data"]["hrs_score"],
        predicted_risk=result["predicted_risk"],
        explanation=result["explanation"],
        recommendations=result["recommendations"],
        alerts=result["alerts"],
        probabilities=result["probabilities"],
        advanced_parameters_used=result["advanced_parameters_used"],
        context_data=result["context_data"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return PredictionResponse(
        hrs_score=result["user_data"]["hrs_score"],
        predicted_risk=result["predicted_risk"],
        bmi_category=result["user_data"]["bmi_category"],
        explanation=result["explanation"],
        recommendations=result["recommendations"],
        alerts=result["alerts"],
        probabilities=result["probabilities"],
        calorie_summary=result["calorie_summary"],
        advanced_parameters_used=result["advanced_parameters_used"],
    )
