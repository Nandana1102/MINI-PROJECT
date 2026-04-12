from __future__ import annotations

from typing import Dict, List

from .features import compute_hrs_components


def generate_recommendations(
    diet_score: float,
    sleep_hours: float,
    activity_level: float,
    bmi: float,
    predicted_risk: str,
    blood_pressure_systolic: int | None = None,
    blood_pressure_diastolic: int | None = None,
    blood_sugar: float | None = None,
    smoking_habit: str | None = None,
    screen_time_hours: float | None = None,
    stress_level: int | None = None,
) -> List[str]:
    recommendations: List[str] = []

    if diet_score < 50:
        recommendations.append("Improve diet quality by adding fruits, vegetables, protein, and reducing junk food.")
    elif diet_score >= 75:
        recommendations.append("Maintain your current healthy diet pattern consistently.")

    if sleep_hours < 7:
        recommendations.append("Increase sleep duration toward 7-8 hours for better recovery and metabolic health.")
    elif sleep_hours > 9:
        recommendations.append("Try to maintain a more balanced sleep duration close to 7-8 hours.")

    if activity_level < 5:
        recommendations.append("Increase physical activity with walking, exercise, or sports at least 30 minutes daily.")
    elif activity_level >= 8:
        recommendations.append("Your physical activity level is strong; continue this active routine.")

    if bmi >= 30:
        recommendations.append("BMI indicates obesity risk. Focus on weight management through diet control and regular exercise.")
    elif bmi >= 25:
        recommendations.append("BMI is above normal range. Gradual lifestyle improvement can reduce future risk.")
    elif bmi < 18.5:
        recommendations.append("BMI is below normal. Consider balanced nutrition and professional guidance if needed.")

    if blood_pressure_systolic is not None and blood_pressure_diastolic is not None:
        if blood_pressure_systolic >= 140 or blood_pressure_diastolic >= 90:
            recommendations.append("Monitor blood pressure regularly, reduce excess salt intake, and seek clinical review if needed.")
        elif blood_pressure_systolic >= 130 or blood_pressure_diastolic >= 80:
            recommendations.append("Elevated blood pressure can be improved through stress control, exercise, and healthier diet choices.")

    if blood_sugar is not None:
        if blood_sugar >= 126:
            recommendations.append("Blood sugar is elevated. Reduce excess sugar intake and consider professional screening.")

    if smoking_habit == "Current Smoker":
        recommendations.append("Smoking cessation is one of the most effective ways to reduce long-term health risk.")

    if screen_time_hours is not None and screen_time_hours >= 8:
        recommendations.append("Reduce prolonged screen time and include short movement breaks throughout the day.")

    if stress_level is not None:
        if stress_level >= 8:
            recommendations.append("Adopt stress management methods such as relaxation, breaks, breathing exercises, or counseling support.")
        elif stress_level >= 6:
            recommendations.append("Moderate stress can be reduced with better routine planning, sleep, and physical activity.")

    if predicted_risk == "High":
        recommendations.append("High risk prediction suggests early medical consultation and regular monitoring.")
    elif predicted_risk == "Moderate":
        recommendations.append("Moderate risk can often be reduced through consistent lifestyle improvement and follow-up checks.")
    else:
        recommendations.append("Low risk is encouraging. Continue maintaining healthy habits.")

    if not recommendations:
        recommendations.append("Continue a balanced lifestyle and routine health monitoring.")

    deduplicated: List[str] = []
    seen = set()
    for item in recommendations:
        if item not in seen:
            deduplicated.append(item)
            seen.add(item)
    return deduplicated


def generate_explainability_text(diet_score: float, sleep_hours: float, activity_level: float, bmi: float) -> str:
    components: Dict[str, float] = compute_hrs_components(diet_score, sleep_hours, activity_level, bmi)
    risk_parts = {
        "poor diet": components["diet_risk"],
        "sleep imbalance": components["sleep_risk"],
        "low physical activity": components["activity_risk"],
        "BMI deviation": components["bmi_risk"],
    }

    sorted_parts = sorted(risk_parts.items(), key=lambda item: item[1], reverse=True)
    top_negative = [name for name, score in sorted_parts[:2] if score > 0.35]
    positive_parts = [name for name, score in sorted_parts if score < 0.2]

    if top_negative:
        primary = " and ".join(top_negative)
        message = f"Main factors increasing risk are {primary}."
    else:
        message = "No single factor is strongly increasing risk; overall balance looks reasonable."

    if positive_parts:
        message += f" Protective factor(s): {', '.join(positive_parts[:2])}."

    if bmi >= 30 and sleep_hours < 6.5:
        message += " High BMI and low sleep together can significantly elevate health risk."
    elif diet_score >= 75 and activity_level >= 7:
        message += " Good diet and strong activity level are helping reduce risk."

    return message
