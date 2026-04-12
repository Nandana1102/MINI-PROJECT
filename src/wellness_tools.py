from __future__ import annotations

from typing import Dict


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def calculate_diet_score(
    fruits_veg_servings: int,
    junk_food_meals_per_week: int,
    sugary_drinks_per_week: int,
    water_liters_per_day: float,
    breakfast_days_per_week: int,
    protein_days_per_week: int,
) -> Dict[str, float]:
    fruits_score = clamp((fruits_veg_servings / 5) * 25, 0, 25)
    water_score = clamp((water_liters_per_day / 3.0) * 15, 0, 15)
    breakfast_score = clamp((breakfast_days_per_week / 7) * 15, 0, 15)
    protein_score = clamp((protein_days_per_week / 7) * 20, 0, 20)
    junk_penalty = clamp((junk_food_meals_per_week / 14) * 15, 0, 15)
    sugary_penalty = clamp((sugary_drinks_per_week / 14) * 10, 0, 10)

    total_score = fruits_score + water_score + breakfast_score + protein_score + (15 - junk_penalty) + (10 - sugary_penalty)
    total_score = round(clamp(total_score, 0, 100), 2)

    return {
        "diet_score": total_score,
        "fruits_veg_score": round(fruits_score, 2),
        "water_score": round(water_score, 2),
        "breakfast_score": round(breakfast_score, 2),
        "protein_score": round(protein_score, 2),
        "junk_food_penalty": round(junk_penalty, 2),
        "sugary_drinks_penalty": round(sugary_penalty, 2),
    }


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = max(height_cm / 100.0, 0.5)
    bmi = weight_kg / (height_m ** 2)
    return round(float(bmi), 2)


def estimate_daily_calories(age: int, gender: str, height_cm: float, weight_kg: float, activity_level: str) -> Dict[str, float | str]:
    gender_key = gender.strip().lower()
    if gender_key == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9,
    }

    multiplier = activity_multipliers.get(activity_level, 1.55)
    maintenance_calories = bmr * multiplier

    return {
        "bmr": round(float(bmr), 2),
        "maintenance_calories": round(float(maintenance_calories), 2),
        "weight_loss_target": round(float(maintenance_calories - 400), 2),
        "weight_gain_target": round(float(maintenance_calories + 300), 2),
        "activity_multiplier": multiplier,
    }


def calorie_guidance_text(calorie_info: Dict[str, float | str]) -> str:
    return (
        f"Estimated BMR is {calorie_info['bmr']} kcal/day and estimated maintenance calories are "
        f"{calorie_info['maintenance_calories']} kcal/day. For gradual weight loss, a target around "
        f"{calorie_info['weight_loss_target']} kcal/day may be used; for gradual weight gain, around "
        f"{calorie_info['weight_gain_target']} kcal/day may be considered."
    )
