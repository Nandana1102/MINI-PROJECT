from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List


PHASE_NAME_TRANSLATIONS = {
    "menstrual": {"en": "Menstrual Phase", "hi": "मासिक धर्म चरण"},
    "follicular": {"en": "Follicular Phase", "hi": "फॉलिक्युलर चरण"},
    "ovulation": {"en": "Ovulation Window", "hi": "ओव्यूलेशन विंडो"},
    "luteal": {"en": "Luteal Phase", "hi": "ल्यूटियल चरण"},
}


PHASE_GUIDANCE = {
    "menstrual": {
        "en": {
            "body_changes": [
                "You may feel lower energy, cramps, back pain, or body heaviness.",
                "Mood sensitivity, irritability, or emotional withdrawal can be more noticeable.",
                "Appetite and sleep quality may temporarily change during this phase.",
            ],
            "precautions": [
                "Prioritize rest, hydration, and iron-rich foods.",
                "Use light movement, stretching, or heat support if cramps occur.",
                "Track severe pain, very heavy bleeding, or dizziness and seek medical advice if needed.",
            ],
        },
        "hi": {
            "body_changes": [
                "इस चरण में ऊर्जा कम लगना, पेट दर्द, पीठ दर्द या शरीर में भारीपन महसूस हो सकता है।",
                "मूड संवेदनशीलता, चिड़चिड़ापन या भावनात्मक बदलाव अधिक दिख सकते हैं।",
                "भूख और नींद के पैटर्न में अस्थायी बदलाव हो सकते हैं।",
            ],
            "precautions": [
                "आराम, पर्याप्त पानी और आयरन-समृद्ध भोजन को प्राथमिकता दें।",
                "दर्द होने पर हल्की गतिविधि, स्ट्रेचिंग या गर्माहट मदद कर सकती है।",
                "यदि बहुत अधिक दर्द, अत्यधिक रक्तस्राव या चक्कर हों तो डॉक्टर से सलाह लें।",
            ],
        },
    },
    "follicular": {
        "en": {
            "body_changes": [
                "Energy, focus, and motivation may gradually improve after the period ends.",
                "Mood often feels lighter and exercise tolerance may be better.",
                "This phase is commonly associated with rebuilding energy and routine stability.",
            ],
            "precautions": [
                "Use this phase for planning, exercise consistency, and balanced nutrition.",
                "Do not skip meals just because energy feels better.",
                "Maintain hydration and sleep rhythm to support hormone balance.",
            ],
        },
        "hi": {
            "body_changes": [
                "पीरियड के बाद ऊर्जा, एकाग्रता और प्रेरणा धीरे-धीरे बेहतर हो सकती है।",
                "मूड हल्का महसूस हो सकता है और व्यायाम सहनशीलता बेहतर हो सकती है।",
                "यह चरण अक्सर ऊर्जा दोबारा बनने और दिनचर्या स्थिर करने से जुड़ा होता है।",
            ],
            "precautions": [
                "इस चरण का उपयोग योजना, नियमित व्यायाम और संतुलित भोजन के लिए करें।",
                "ऊर्जा बेहतर लगे तो भी भोजन छोड़ने से बचें।",
                "हार्मोन संतुलन के लिए पानी और नींद की नियमितता बनाए रखें।",
            ],
        },
    },
    "ovulation": {
        "en": {
            "body_changes": [
                "Some users notice higher confidence, social energy, or libido around ovulation.",
                "Mild bloating, pelvic discomfort, or cervical discharge changes may occur.",
                "Body temperature and sensitivity to hormonal fluctuations can shift slightly.",
            ],
            "precautions": [
                "Stay hydrated and monitor unusual pain if it appears suddenly.",
                "Use good sleep and nutrition habits to avoid unnecessary fatigue.",
                "Remember that ovulation timing is approximate and can vary between cycles.",
            ],
        },
        "hi": {
            "body_changes": [
                "कुछ लोगों को ओव्यूलेशन के आसपास आत्मविश्वास, सामाजिक ऊर्जा या इच्छा में वृद्धि महसूस हो सकती है।",
                "हल्की सूजन, पेल्विक असुविधा या डिस्चार्ज में बदलाव हो सकते हैं।",
                "शरीर का तापमान और हार्मोनल बदलावों के प्रति संवेदनशीलता थोड़ी बदल सकती है।",
            ],
            "precautions": [
                "पानी पर्याप्त लें और अचानक दर्द होने पर ध्यान रखें।",
                "थकान से बचने के लिए नींद और पोषण की अच्छी आदतें बनाए रखें।",
                "याद रखें कि ओव्यूलेशन की तारीख अनुमानित होती है और हर चक्र में बदल सकती है।",
            ],
        },
    },
    "luteal": {
        "en": {
            "body_changes": [
                "This phase is commonly linked with PMS-like symptoms such as bloating, cravings, breast tenderness, and fatigue.",
                "Emotional changes such as irritability, sadness, anxiety, or frustration can increase in this phase.",
                "You may feel sudden mood shifts even if nothing major has changed externally.",
            ],
            "precautions": [
                "Reduce excessive salt, highly processed foods, and extra caffeine if they worsen symptoms.",
                "Use sleep, hydration, light activity, and emotional self-awareness to manage mood changes.",
                "If emotional symptoms are severe or repeatedly disruptive, consider professional advice.",
            ],
        },
        "hi": {
            "body_changes": [
                "यह चरण अक्सर PMS जैसे लक्षणों से जुड़ा होता है, जैसे सूजन, cravings, स्तनों में दर्द और थकान।",
                "इस चरण में चिड़चिड़ापन, उदासी, चिंता या निराशा जैसे भावनात्मक बदलाव बढ़ सकते हैं।",
                "कई बार बाहर कुछ बड़ा न बदलने पर भी अचानक मूड स्विंग महसूस हो सकता है।",
            ],
            "precautions": [
                "यदि नमक, प्रोसेस्ड फूड या अतिरिक्त कैफीन लक्षण बढ़ाते हों तो उन्हें कम करें।",
                "मूड बदलाव सँभालने के लिए नींद, पानी, हल्की गतिविधि और self-awareness का उपयोग करें।",
                "यदि भावनात्मक लक्षण बहुत अधिक हों या बार-बार जीवन को प्रभावित करें तो विशेषज्ञ सलाह लें।",
            ],
        },
    },
}


def translate_phase_name(phase_key: str, lang: str = "en") -> str:
    return PHASE_NAME_TRANSLATIONS.get(phase_key, {}).get(lang, phase_key.replace("_", " ").title())


def get_phase_guidance(phase_key: str, lang: str = "en") -> Dict[str, List[str]]:
    payload = PHASE_GUIDANCE.get(phase_key, {})
    return payload.get(lang, payload.get("en", {"body_changes": [], "precautions": []}))


def _phase_date_range(cycle_start: date, start_day: int, end_day: int) -> tuple[date, date]:
    start_date = cycle_start + timedelta(days=max(start_day - 1, 0))
    end_date = cycle_start + timedelta(days=max(end_day - 1, 0))
    return start_date, end_date


def predict_cycle_phases(
    last_period_start: date,
    cycle_length: int = 28,
    period_length: int = 5,
    current_date: date | None = None,
    lang: str = "en",
) -> Dict[str, Any]:
    current_date = current_date or date.today()
    cycle_length = max(21, min(40, int(cycle_length)))
    period_length = max(2, min(int(period_length), cycle_length - 7))

    if current_date >= last_period_start:
        cycles_elapsed = (current_date - last_period_start).days // cycle_length
        current_cycle_start = last_period_start + timedelta(days=cycles_elapsed * cycle_length)
    else:
        current_cycle_start = last_period_start

    days_since_cycle_start = (current_date - current_cycle_start).days
    cycle_day = max(1, min(cycle_length, days_since_cycle_start + 1)) if current_date >= current_cycle_start else 1

    ovulation_day = max(period_length + 2, cycle_length - 14)
    ovulation_start_day = max(period_length + 1, ovulation_day - 2)
    ovulation_end_day = min(cycle_length, ovulation_day + 1)
    follicular_start_day = period_length + 1
    follicular_end_day = max(follicular_start_day, ovulation_start_day - 1)
    luteal_start_day = min(cycle_length, ovulation_end_day + 1)

    phases = [
        {"key": "menstrual", "start_day": 1, "end_day": period_length},
        {"key": "follicular", "start_day": follicular_start_day, "end_day": follicular_end_day},
        {"key": "ovulation", "start_day": ovulation_start_day, "end_day": ovulation_end_day},
        {"key": "luteal", "start_day": luteal_start_day, "end_day": cycle_length},
    ]

    if cycle_day <= period_length:
        current_phase_key = "menstrual"
    elif cycle_day <= follicular_end_day:
        current_phase_key = "follicular"
    elif cycle_day <= ovulation_end_day:
        current_phase_key = "ovulation"
    else:
        current_phase_key = "luteal"

    phase_rows = []
    for phase in phases:
        start_date, end_date = _phase_date_range(current_cycle_start, phase["start_day"], phase["end_day"])
        guidance = get_phase_guidance(phase["key"], lang)
        phase_rows.append(
            {
                "key": phase["key"],
                "display_name": translate_phase_name(phase["key"], lang),
                "start_day": phase["start_day"],
                "end_day": phase["end_day"],
                "start_date": start_date,
                "end_date": end_date,
                "body_changes": guidance.get("body_changes", []),
                "precautions": guidance.get("precautions", []),
            }
        )

    next_expected_period = current_cycle_start + timedelta(days=cycle_length)
    current_cycle_end = next_expected_period - timedelta(days=1)
    days_until_next_period = (next_expected_period - current_date).days

    current_phase = next(item for item in phase_rows if item["key"] == current_phase_key)

    return {
        "current_cycle_start": current_cycle_start,
        "current_cycle_end": current_cycle_end,
        "next_expected_period": next_expected_period,
        "cycle_length": cycle_length,
        "period_length": period_length,
        "cycle_day": cycle_day,
        "days_until_next_period": max(days_until_next_period, 0),
        "current_phase": current_phase,
        "phases": phase_rows,
    }
