from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user", server_default="user")
    preferred_language = Column(String(10), nullable=False, default="en", server_default="en")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    diet_score = Column(Float, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    activity_level = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    bmi_category = Column(String(50), nullable=False)
    hrs_score = Column(Float, nullable=False)
    predicted_risk = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False, default=list)
    alerts = Column(JSON, nullable=False, default=list)
    probabilities = Column(JSON, nullable=False, default=dict)
    advanced_parameters_used = Column(Boolean, default=False, nullable=False)
    context_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="predictions")
