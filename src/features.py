from __future__ import annotations

from typing import Dict

from .utils import bmi_category, clamp_zero_one, normalize


def compute_hrs_components(diet_score: float, sleep_hours: float, activity_level: float, bmi: float) -> Dict[str, float]:
    diet_norm = normalize(diet_score, 0, 100)
    activity_norm = normalize(activity_level, 0, 10)
    bmi_norm = normalize(bmi, 15, 40)

    diet_risk = 1 - diet_norm
    sleep_risk = clamp_zero_one(abs(sleep_hours - 7.5) / 3.5)
    activity_risk = 1 - activity_norm

    healthy_bmi_center = 22.0
    bmi_risk = clamp_zero_one(abs(bmi - healthy_bmi_center) / 12.0)

    return {
        "diet_risk": diet_risk,
        "sleep_risk": sleep_risk,
        "activity_risk": activity_risk,
        "bmi_risk": bmi_risk,
        "diet_norm": diet_norm,
        "activity_norm": activity_norm,
        "bmi_norm": bmi_norm,
    }


def compute_hrs_score(diet_score: float, sleep_hours: float, activity_level: float, bmi: float) -> float:
    components = compute_hrs_components(diet_score, sleep_hours, activity_level, bmi)
    hrs = (
        0.25 * components["diet_risk"]
        + 0.20 * components["sleep_risk"]
        + 0.20 * components["activity_risk"]
        + 0.35 * components["bmi_risk"]
    ) * 100
    return round(float(hrs), 2)


def build_user_feature_dict(diet_score: float, sleep_hours: float, activity_level: float, bmi: float) -> Dict[str, float | str]:
    hrs_score = compute_hrs_score(diet_score, sleep_hours, activity_level, bmi)
    return {
        "diet_score": float(diet_score),
        "sleep_hours": float(sleep_hours),
        "activity_level": float(activity_level),
        "bmi": float(bmi),
        "hrs_score": float(hrs_score),
        "bmi_category": bmi_category(float(bmi)),
    }
