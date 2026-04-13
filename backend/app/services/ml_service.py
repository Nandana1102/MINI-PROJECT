from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

import pandas as pd

from src.alerts import generate_health_alerts
from src.features import build_user_feature_dict
from src.modeling import load_bundle, predict_single, train_and_save
from src.recommendations import generate_explainability_text, generate_recommendations
from src.utils import FEATURE_COLUMNS, model_bundle_path
from src.wellness_tools import calorie_guidance_text, estimate_daily_calories


@lru_cache(maxsize=1)
def get_model_bundle() -> Dict[str, Any]:
    if not model_bundle_path().exists():
        return train_and_save(n_samples=1000, random_state=42)
    return load_bundle()


def run_prediction(payload: Dict[str, Any]) -> Dict[str, Any]:
    model_bundle = get_model_bundle()
    core_values = {
        "diet_score": float(payload["diet_score"]),
        "sleep_hours": float(payload["sleep_hours"]),
        "activity_level": float(payload["activity_level"]),
        "bmi": float(payload["bmi"]),
    }
    user_data = build_user_feature_dict(**core_values)
    input_df = pd.DataFrame([{feature: user_data[feature] for feature in FEATURE_COLUMNS}])
    model_name = payload.get("model_name", "Random Forest")
    predicted_risk, probabilities = predict_single(model_bundle, input_df, model_name)
    explanation = generate_explainability_text(**core_values)

    advanced_parameters_used = any(
        payload.get(key) is not None
        for key in [
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "blood_sugar",
            "smoking_habit",
            "screen_time_hours",
            "stress_level",
        ]
    )

    recommendations = generate_recommendations(
        predicted_risk=predicted_risk,
        blood_pressure_systolic=payload.get("blood_pressure_systolic"),
        blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
        blood_sugar=payload.get("blood_sugar"),
        smoking_habit=payload.get("smoking_habit"),
        screen_time_hours=payload.get("screen_time_hours"),
        stress_level=payload.get("stress_level"),
        **core_values,
    )
    alerts = generate_health_alerts(
        predicted_risk=predicted_risk,
        blood_pressure_systolic=payload.get("blood_pressure_systolic"),
        blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
        blood_sugar=payload.get("blood_sugar"),
        smoking_habit=payload.get("smoking_habit"),
        screen_time_hours=payload.get("screen_time_hours"),
        stress_level=payload.get("stress_level"),
        sleep_hours=core_values["sleep_hours"],
        bmi=core_values["bmi"],
    )

    calorie_summary = None
    if all(payload.get(key) is not None for key in ["age", "gender", "height_cm", "weight_kg", "calorie_activity"]):
        calorie_info = estimate_daily_calories(
            age=int(payload["age"]),
            gender=str(payload["gender"]),
            height_cm=float(payload["height_cm"]),
            weight_kg=float(payload["weight_kg"]),
            activity_level=str(payload["calorie_activity"]),
        )
        calorie_summary = calorie_guidance_text(calorie_info)

    return {
        "model_name": model_name,
        "user_data": user_data,
        "predicted_risk": predicted_risk,
        "explanation": explanation,
        "recommendations": recommendations,
        "alerts": [message for _, message in alerts],
        "probabilities": {label: float(prob) for label, prob in zip(model_bundle["label_classes"], probabilities)},
        "calorie_summary": calorie_summary,
        "advanced_parameters_used": advanced_parameters_used,
        "context_data": {
            key: payload.get(key)
            for key in [
                "age",
                "gender",
                "height_cm",
                "weight_kg",
                "calorie_activity",
                "blood_pressure_systolic",
                "blood_pressure_diastolic",
                "blood_sugar",
                "smoking_habit",
                "screen_time_hours",
                "stress_level",
            ]
        },
    }
