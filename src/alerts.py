from __future__ import annotations

from typing import List, Tuple


AlertItem = Tuple[str, str]


def generate_health_alerts(
    sleep_hours: float,
    bmi: float,
    predicted_risk: str,
    blood_pressure_systolic: int | None = None,
    blood_pressure_diastolic: int | None = None,
    blood_sugar: float | None = None,
    smoking_habit: str | None = None,
    screen_time_hours: float | None = None,
    stress_level: int | None = None,
) -> List[AlertItem]:
    alerts: List[AlertItem] = []

    if bmi >= 30:
        alerts.append(("error", "Your BMI is in the obese range. Weight management and lifestyle intervention are strongly recommended."))
    elif bmi >= 25:
        alerts.append(("warning", "Your BMI is in the overweight range. Gradual improvement can reduce long-term health risk."))
    elif bmi < 18.5:
        alerts.append(("warning", "Your BMI is in the underweight range. Nutritional balance should be reviewed."))

    if sleep_hours < 5.5:
        alerts.append(("error", "Sleep is critically low. Very low sleep can increase fatigue, metabolic stress, and overall health risk."))
    elif sleep_hours < 7:
        alerts.append(("warning", "Sleep is below the recommended range. Aim for around 7 to 8 hours."))
    elif sleep_hours > 9.5:
        alerts.append(("warning", "Sleep duration is unusually high. Check for poor sleep quality or irregular routine."))

    if blood_pressure_systolic is not None and blood_pressure_diastolic is not None:
        if blood_pressure_systolic >= 140 or blood_pressure_diastolic >= 90:
            alerts.append(("error", "Blood pressure is in a high range. Regular monitoring and medical advice are recommended."))
        elif blood_pressure_systolic >= 130 or blood_pressure_diastolic >= 80:
            alerts.append(("warning", "Blood pressure is elevated and should be monitored carefully."))

    if blood_sugar is not None:
        if blood_sugar >= 200:
            alerts.append(("error", "Blood sugar level is very high. Immediate monitoring and professional consultation are advised."))
        elif blood_sugar >= 126:
            alerts.append(("warning", "Blood sugar appears elevated and should be reviewed with proper testing."))

    if smoking_habit == "Current Smoker":
        alerts.append(("error", "Smoking habit is a major health risk factor and can worsen long-term outcomes."))
    elif smoking_habit == "Former Smoker":
        alerts.append(("info", "Former smoking history should still be considered in long-term health monitoring."))

    if screen_time_hours is not None and screen_time_hours >= 8:
        alerts.append(("warning", "Screen time is high and may reflect sedentary behavior. Consider regular movement breaks."))

    if stress_level is not None:
        if stress_level >= 8:
            alerts.append(("error", "Stress level is very high. Stress management and recovery strategies are important."))
        elif stress_level >= 6:
            alerts.append(("warning", "Stress level is moderately high. Relaxation, sleep hygiene, and workload balance may help."))

    if predicted_risk == "High":
        alerts.append(("error", "Overall predicted health risk is High. Early intervention and follow-up are recommended."))
    elif predicted_risk == "Moderate":
        alerts.append(("warning", "Overall predicted health risk is Moderate. Improvement in lifestyle factors can reduce future risk."))

    if not alerts:
        alerts.append(("success", "No major immediate alert was detected from the current inputs."))

    return alerts
