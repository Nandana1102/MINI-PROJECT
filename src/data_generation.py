from __future__ import annotations

import numpy as np
import pandas as pd

from .features import compute_hrs_score
from .utils import TARGET_COLUMN, bmi_category


RANDOM_SEED = 42


def _categorize_risk(risk_value: float) -> str:
    if risk_value < 38:
        return "Low"
    if risk_value < 63:
        return "Moderate"
    return "High"


def generate_dataset(n_samples: int = 1000, random_state: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    diet_score = np.clip(rng.normal(58, 18, n_samples), 10, 100)
    sleep_hours = np.clip(rng.normal(7.0, 1.2, n_samples), 3.5, 10)
    activity_level = np.clip(rng.normal(5.2, 2.2, n_samples), 0, 10)
    bmi = np.clip(rng.normal(25.2, 4.8, n_samples), 15.5, 40)

    data = []
    for i in range(n_samples):
        hrs_score = compute_hrs_score(
            float(diet_score[i]),
            float(sleep_hours[i]),
            float(activity_level[i]),
            float(bmi[i]),
        )

        latent_risk = hrs_score
        if bmi[i] >= 30:
            latent_risk += 10
        elif bmi[i] < 18.5:
            latent_risk += 4

        if sleep_hours[i] < 6:
            latent_risk += 8
        elif sleep_hours[i] > 9:
            latent_risk += 4

        if diet_score[i] < 40:
            latent_risk += 6
        if activity_level[i] < 3:
            latent_risk += 7
        if diet_score[i] > 75 and activity_level[i] > 7 and 18.5 <= bmi[i] < 25:
            latent_risk -= 8

        latent_risk += rng.normal(0, 3.5)
        latent_risk = float(np.clip(latent_risk, 5, 95))

        data.append(
            {
                "diet_score": round(float(diet_score[i]), 2),
                "sleep_hours": round(float(sleep_hours[i]), 2),
                "activity_level": round(float(activity_level[i]), 2),
                "bmi": round(float(bmi[i]), 2),
                "hrs_score": round(float(hrs_score), 2),
                "bmi_category": bmi_category(float(bmi[i])),
                TARGET_COLUMN: _categorize_risk(latent_risk),
            }
        )

    return pd.DataFrame(data)
