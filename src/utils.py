from __future__ import annotations

from pathlib import Path
from typing import Dict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
PLOTS_DIR = BASE_DIR / "plots"

for directory in [DATA_DIR, MODELS_DIR, REPORTS_DIR, PLOTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


FEATURE_COLUMNS = ["diet_score", "sleep_hours", "activity_level", "bmi", "hrs_score"]
RAW_FEATURE_COLUMNS = ["diet_score", "sleep_hours", "activity_level", "bmi"]
TARGET_COLUMN = "health_risk_category"
CLASS_ORDER = ["Low", "Moderate", "High"]


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def normalize(value: float, min_value: float, max_value: float) -> float:
    value = max(min_value, min(max_value, value))
    return (value - min_value) / (max_value - min_value)


def clamp_zero_one(value: float) -> float:
    return max(0.0, min(1.0, value))


def model_bundle_path() -> Path:
    return MODELS_DIR / "health_risk_bundle.joblib"


def dataset_path() -> Path:
    return DATA_DIR / "health_risk_dataset.csv"


def risk_color(risk: str) -> str:
    mapping: Dict[str, str] = {
        "Low": "#16a34a",
        "Moderate": "#f59e0b",
        "High": "#dc2626",
    }
    return mapping.get(risk, "#2563eb")
