from __future__ import annotations

from datetime import datetime
from typing import List, Sequence, Tuple


def build_text_report(
    diet_score: float,
    sleep_hours: float,
    activity_level: float,
    bmi: float,
    bmi_category: str,
    hrs_score: float,
    predicted_risk: str,
    model_name: str,
    explainability_text: str,
    recommendations: List[str],
    additional_sections: Sequence[Tuple[str, str]] | None = None,
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recommendations_text = "\n".join(f"- {item}" for item in recommendations)

    extra_text = ""
    if additional_sections:
        formatted_sections = []
        for section_title, section_body in additional_sections:
            formatted_sections.append(f"{section_title}\n{section_body}")
        extra_text = "\n\n" + "\n\n".join(formatted_sections)

    return f"""Health Risk Assessment Report
Generated on: {timestamp}

INPUT DETAILS
- Diet Score: {diet_score}
- Sleep Hours: {sleep_hours}
- Physical Activity Level: {activity_level}
- BMI: {bmi}
- BMI Category: {bmi_category}

SYSTEM OUTPUT
- Health Risk Score (HRS): {hrs_score}
- Predicted Health Risk Category: {predicted_risk}
- Model Used: {model_name}

EXPLAINABILITY SUMMARY
{explainability_text}

PERSONALIZED RECOMMENDATIONS
{recommendations_text}{extra_text}

NOTE
This project is an academic predictive analytics system and not a replacement for clinical diagnosis.
"""
