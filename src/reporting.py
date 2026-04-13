from __future__ import annotations

from datetime import datetime
from typing import List, Sequence, Tuple

from .translations import t, translate_bmi_category, translate_model_name, translate_risk


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
    lang: str = "en",
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recommendations_text = "\n".join(f"- {item}" for item in recommendations)

    extra_text = ""
    if additional_sections:
        formatted_sections = []
        for section_title, section_body in additional_sections:
            formatted_sections.append(f"{section_title}\n{section_body}")
        extra_text = "\n\n" + "\n\n".join(formatted_sections)

    return f"""{t('report_title', lang)}
{t('report_generated_on', lang, timestamp=timestamp)}

{t('report_input_details', lang)}
- {t('diet_score', lang)}: {diet_score}
- {t('sleep_hours', lang)}: {sleep_hours}
- {t('activity_level', lang)}: {activity_level}
- BMI: {bmi}
- {t('bmi_category', lang)}: {translate_bmi_category(bmi_category, lang)}

{t('report_system_output', lang)}
- {t('hrs_score', lang)}: {hrs_score}
- {t('predicted_risk', lang)}: {translate_risk(predicted_risk, lang)}
- {t('selected_model', lang)}: {translate_model_name(model_name, lang)}

{t('report_explainability', lang)}
{explainability_text}

{t('report_recommendations', lang)}
{recommendations_text}{extra_text}

{t('report_note', lang)}
{t('report_note_text', lang)}
"""
