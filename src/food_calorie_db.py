from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

import pandas as pd

from .utils import DATA_DIR


FOOD_CALORIE_DB_PATH = DATA_DIR / "food_calorie_reference.csv"


@lru_cache(maxsize=1)
def load_food_calorie_db() -> pd.DataFrame:
    dataframe = pd.read_csv(FOOD_CALORIE_DB_PATH)
    dataframe["food_name"] = dataframe["food_name"].astype(str)
    dataframe["serving_size"] = dataframe["serving_size"].astype(str)
    dataframe["food_category"] = dataframe["food_category"].astype(str)
    dataframe["healthier_alternative"] = dataframe["healthier_alternative"].astype(str)
    dataframe["estimated_calories"] = pd.to_numeric(dataframe["estimated_calories"], errors="coerce").fillna(0)
    return dataframe


def list_supported_foods() -> List[str]:
    dataframe = load_food_calorie_db()
    return dataframe["food_name"].tolist()


def get_food_info(food_name: str) -> Dict[str, Any] | None:
    dataframe = load_food_calorie_db()
    matched = dataframe[dataframe["food_name"].str.lower() == str(food_name).strip().lower()]
    if matched.empty:
        return None

    payload = matched.iloc[0].to_dict()
    payload["estimated_calories"] = int(round(float(payload.get("estimated_calories", 0))))
    payload["risk_flags"] = [
        flag.strip()
        for flag in str(payload.get("risk_flags", "")).split(",")
        if flag.strip()
    ]
    return payload
