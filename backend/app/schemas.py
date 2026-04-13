from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=100)
    preferred_language: Literal["en", "hi"] = "en"


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    preferred_language: str = "en"
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLanguagePreferenceUpdate(BaseModel):
    preferred_language: Literal["en", "hi"]


class PredictionRequest(BaseModel):
    model_name: str = "Random Forest"
    diet_score: float = Field(ge=0, le=100)
    sleep_hours: float = Field(ge=3, le=10)
    activity_level: float = Field(ge=0, le=10)
    bmi: float = Field(ge=15, le=40)
    age: Optional[int] = Field(default=None, ge=15, le=90)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, ge=120, le=220)
    weight_kg: Optional[float] = Field(default=None, ge=30, le=180)
    calorie_activity: Optional[str] = None
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=80, le=220)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=50, le=140)
    blood_sugar: Optional[float] = Field(default=None, ge=60, le=350)
    smoking_habit: Optional[str] = None
    screen_time_hours: Optional[float] = Field(default=None, ge=0, le=16)
    stress_level: Optional[int] = Field(default=None, ge=0, le=10)


class PredictionResponse(BaseModel):
    hrs_score: float
    predicted_risk: str
    bmi_category: str
    explanation: str
    recommendations: List[str]
    alerts: List[str]
    probabilities: Dict[str, float]
    calorie_summary: Optional[str] = None
    advanced_parameters_used: bool


class PredictionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_name: str
    diet_score: float
    sleep_hours: float
    activity_level: float
    bmi: float
    bmi_category: str
    hrs_score: float
    predicted_risk: str
    explanation: str
    recommendations: List[str]
    alerts: List[str]
    probabilities: Dict[str, float]
    advanced_parameters_used: bool
    context_data: Optional[Dict[str, Any]] = None
    created_at: datetime


class AdminDashboardStats(BaseModel):
    total_users: int
    total_admins: int
    total_predictions: int
    risk_distribution: Dict[str, int]
    recent_users: List[UserRead]
    recent_predictions: List[PredictionHistoryItem]
