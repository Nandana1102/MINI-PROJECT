from __future__ import annotations

import re
from collections import defaultdict
from io import BytesIO
from typing import Any, Dict, List

import numpy as np
from PIL import Image

from .food_calorie_db import get_food_info, list_supported_foods


PORTION_MULTIPLIERS = {
    "Small": 0.75,
    "Standard": 1.0,
    "Large": 1.35,
}

FOOD_NAME_TRANSLATIONS = {
    "apple": {"en": "Apple", "hi": "सेब"},
    "banana": {"en": "Banana", "hi": "केला"},
    "salad": {"en": "Salad", "hi": "सलाद"},
    "idli": {"en": "Idli", "hi": "इडली"},
    "dosa": {"en": "Dosa", "hi": "डोसा"},
    "vada": {"en": "Vada", "hi": "वड़ा"},
    "pongal": {"en": "Pongal", "hi": "पोंगल"},
    "upma": {"en": "Upma", "hi": "उपमा"},
    "uttapam": {"en": "Uttapam", "hi": "उत्तपम"},
    "chapati": {"en": "Chapati", "hi": "चपाती"},
    "rice": {"en": "Rice", "hi": "चावल"},
    "lemon rice": {"en": "Lemon Rice", "hi": "लेमन राइस"},
    "curd rice": {"en": "Curd Rice", "hi": "दही चावल"},
    "sambar rice": {"en": "Sambar Rice", "hi": "सांभर चावल"},
    "biryani": {"en": "Biryani", "hi": "बिरयानी"},
    "sandwich": {"en": "Sandwich", "hi": "सैंडविच"},
    "noodles": {"en": "Noodles", "hi": "नूडल्स"},
    "samosa": {"en": "Samosa", "hi": "समोसा"},
    "pizza": {"en": "Pizza", "hi": "पिज़्ज़ा"},
    "burger": {"en": "Burger", "hi": "बर्गर"},
    "french fries": {"en": "French Fries", "hi": "फ्रेंच फ्राइज़"},
    "grilled chicken": {"en": "Grilled Chicken", "hi": "ग्रिल्ड चिकन"},
    "ice cream": {"en": "Ice Cream", "hi": "आइस क्रीम"},
}

PORTION_TRANSLATIONS = {
    "Small": {"en": "Small", "hi": "छोटी मात्रा"},
    "Standard": {"en": "Standard", "hi": "मानक मात्रा"},
    "Large": {"en": "Large", "hi": "बड़ी मात्रा"},
}

DECISION_TRANSLATIONS = {
    "Recommended": {"en": "Recommended", "hi": "अनुशंसित"},
    "Consume in moderation": {"en": "Consume in moderation", "hi": "सीमित मात्रा में लें"},
    "Better avoid frequently": {"en": "Better avoid frequently", "hi": "बार-बार लेने से बचें"},
}

CUISINE_HINT_TRANSLATIONS = {
    "Auto": {"en": "Auto", "hi": "ऑटो"},
    "South Indian": {"en": "South Indian", "hi": "दक्षिण भारतीय"},
    "Healthy & Fruit": {"en": "Healthy & Fruit", "hi": "स्वस्थ / फल"},
    "Meals": {"en": "Meals", "hi": "मुख्य भोजन"},
    "Fast Food": {"en": "Fast Food", "hi": "फास्ट फूड"},
    "Snacks & Dessert": {"en": "Snacks & Dessert", "hi": "स्नैक्स / डेज़र्ट"},
}

CUISINE_FOOD_GROUPS = {
    "Auto": [],
    "South Indian": ["idli", "dosa", "vada", "pongal", "upma", "uttapam", "rice", "lemon rice", "curd rice", "sambar rice", "biryani"],
    "Healthy & Fruit": ["salad", "apple", "banana", "grilled chicken"],
    "Meals": ["chapati", "rice", "lemon rice", "curd rice", "sambar rice", "biryani", "noodles", "grilled chicken"],
    "Fast Food": ["pizza", "burger", "sandwich", "french fries"],
    "Snacks & Dessert": ["vada", "samosa", "ice cream"],
}

FILENAME_KEYWORDS = {
    "apple": ["apple", "apples"],
    "banana": ["banana", "bananas"],
    "salad": ["salad", "greens", "veggies", "vegetable"],
    "idli": ["idli"],
    "dosa": ["dosa", "dosai"],
    "vada": ["vada", "meduvada", "medu_vada"],
    "pongal": ["pongal"],
    "upma": ["upma"],
    "uttapam": ["uttapam", "uthappam"],
    "chapati": ["chapati", "roti"],
    "rice": ["rice", "plainrice", "plain_rice"],
    "lemon rice": ["lemonrice", "lemon_rice"],
    "curd rice": ["curdrice", "curd_rice", "thairsadham"],
    "sambar rice": ["sambarrice", "sambar_rice"],
    "biryani": ["biryani"],
    "sandwich": ["sandwich"],
    "noodles": ["noodles", "noodle"],
    "samosa": ["samosa"],
    "pizza": ["pizza"],
    "burger": ["burger"],
    "french fries": ["fries", "frenchfries", "french_fries"],
    "grilled chicken": ["chicken", "grilledchicken", "grilled_chicken"],
    "ice cream": ["icecream", "ice_cream", "dessert"],
}


def translate_food_name(food_name: str, lang: str = "en") -> str:
    normalized = str(food_name).strip().lower()
    payload = FOOD_NAME_TRANSLATIONS.get(normalized)
    if not payload:
        return str(food_name)
    return payload.get(lang, payload.get("en", str(food_name)))


def translate_portion_size(portion_size: str, lang: str = "en") -> str:
    payload = PORTION_TRANSLATIONS.get(portion_size, {})
    return payload.get(lang, portion_size)


def translate_decision_label(label: str, lang: str = "en") -> str:
    payload = DECISION_TRANSLATIONS.get(label, {})
    return payload.get(lang, label)


def translate_cuisine_hint(cuisine_hint: str, lang: str = "en") -> str:
    payload = CUISINE_HINT_TRANSLATIONS.get(cuisine_hint, {})
    return payload.get(lang, cuisine_hint)


def list_cuisine_hints() -> List[str]:
    return list(CUISINE_FOOD_GROUPS.keys())


def get_ordered_food_options(cuisine_hint: str = "Auto") -> List[str]:
    supported_foods = list_supported_foods()
    prioritized = [food for food in CUISINE_FOOD_GROUPS.get(cuisine_hint, []) if food in supported_foods]
    remaining = [food for food in supported_foods if food not in prioritized]
    return prioritized + remaining


def load_image_from_upload(uploaded_file) -> Image.Image:
    return Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")


def _tokenize_filename(filename: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(filename).lower()).strip()


def _get_candidate_pool(cuisine_hint: str) -> List[str]:
    supported_foods = list_supported_foods()
    if cuisine_hint == "Auto":
        return supported_foods
    pool = [food for food in CUISINE_FOOD_GROUPS.get(cuisine_hint, []) if food in supported_foods]
    return pool or supported_foods


def _image_feature_stats(image: Image.Image) -> Dict[str, float]:
    resized = image.resize((96, 96)).convert("RGB")
    rgb_array = np.asarray(resized, dtype=np.float32)
    red = rgb_array[..., 0]
    green = rgb_array[..., 1]
    blue = rgb_array[..., 2]

    brightness = (red + green + blue) / 3.0
    colorfulness = np.max(rgb_array, axis=2) - np.min(rgb_array, axis=2)
    saturation_like = colorfulness

    white_mask = (brightness > 185) & (saturation_like < 40)
    yellow_mask = (red > 150) & (green > 120) & (blue < 140)
    orange_mask = (red > 150) & (green > 90) & (green < 185) & (blue < 125)
    brown_mask = (red > 110) & (green > 70) & (green < 170) & (blue < 115)
    green_mask = (green > red + 15) & (green > blue + 15)
    red_mask = (red > green + 20) & (red > blue + 20)

    return {
        "red_mean": float(red.mean()),
        "green_mean": float(green.mean()),
        "blue_mean": float(blue.mean()),
        "brightness": float(brightness.mean()),
        "colorfulness": float(colorfulness.mean()),
        "white_fraction": float(white_mask.mean()),
        "yellow_fraction": float(yellow_mask.mean()),
        "orange_fraction": float(orange_mask.mean()),
        "brown_fraction": float(brown_mask.mean()),
        "green_fraction": float(green_mask.mean()),
        "red_fraction": float(red_mask.mean()),
        "aspect_ratio": float(image.width / max(image.height, 1)),
    }


def suggest_food_candidates(filename: str, image: Image.Image | None = None, cuisine_hint: str = "Auto", limit: int = 5) -> List[Dict[str, float | str]]:
    candidate_pool = _get_candidate_pool(cuisine_hint)
    candidate_pool_set = set(candidate_pool)
    normalized_name = _tokenize_filename(filename)
    scores: dict[str, float] = defaultdict(float)

    for food_name in candidate_pool:
        scores[food_name] += 0.02 if cuisine_hint == "Auto" else 0.10

    for food_name, keywords in FILENAME_KEYWORDS.items():
        if food_name not in candidate_pool_set:
            continue
        for keyword in keywords:
            if keyword.replace("_", " ") in normalized_name:
                scores[food_name] += 0.65 + min(len(keyword) / 20.0, 0.2)

    if image is not None:
        stats = _image_feature_stats(image)
        brightness = stats["brightness"]
        colorfulness = stats["colorfulness"]
        white_fraction = stats["white_fraction"]
        yellow_fraction = stats["yellow_fraction"]
        orange_fraction = stats["orange_fraction"]
        brown_fraction = stats["brown_fraction"]
        green_fraction = stats["green_fraction"]
        red_fraction = stats["red_fraction"]
        aspect_ratio = stats["aspect_ratio"]

        if "salad" in candidate_pool_set and green_fraction > 0.18:
            scores["salad"] += 0.55
        if "pizza" in candidate_pool_set and red_fraction > 0.14 and yellow_fraction > 0.08:
            scores["pizza"] += 0.35
        if "burger" in candidate_pool_set and brown_fraction > 0.18 and red_fraction > 0.10:
            scores["burger"] += 0.24
        if "sandwich" in candidate_pool_set and brown_fraction > 0.15 and brightness > 125:
            scores["sandwich"] += 0.18
        if "french fries" in candidate_pool_set and yellow_fraction > 0.22:
            scores["french fries"] += 0.24
        if "biryani" in candidate_pool_set and yellow_fraction > 0.12 and colorfulness > 55:
            scores["biryani"] += 0.42
        if "lemon rice" in candidate_pool_set and yellow_fraction > 0.18 and brightness > 120:
            scores["lemon rice"] += 0.46
        if "sambar rice" in candidate_pool_set and orange_fraction > 0.14:
            scores["sambar rice"] += 0.38
        if "idli" in candidate_pool_set and white_fraction > 0.24:
            scores["idli"] += 0.46
        if "curd rice" in candidate_pool_set and white_fraction > 0.22 and brightness > 170:
            scores["curd rice"] += 0.40
        if "rice" in candidate_pool_set and white_fraction > 0.20:
            scores["rice"] += 0.26
        if "pongal" in candidate_pool_set and white_fraction > 0.16 and yellow_fraction > 0.06:
            scores["pongal"] += 0.30
        if "upma" in candidate_pool_set and white_fraction > 0.12 and brown_fraction < 0.18:
            scores["upma"] += 0.24
        if "dosa" in candidate_pool_set and brown_fraction > 0.18 and 105 <= brightness <= 190:
            scores["dosa"] += 0.32
        if "vada" in candidate_pool_set and brown_fraction > 0.22 and brightness < 180:
            scores["vada"] += 0.34
        if "uttapam" in candidate_pool_set and brown_fraction > 0.14 and green_fraction > 0.04:
            scores["uttapam"] += 0.28
        if "chapati" in candidate_pool_set and brown_fraction > 0.16 and 110 <= brightness <= 180:
            scores["chapati"] += 0.24
        if "noodles" in candidate_pool_set and yellow_fraction > 0.10 and brown_fraction > 0.10:
            scores["noodles"] += 0.20
        if "grilled chicken" in candidate_pool_set and brown_fraction > 0.18 and red_fraction < 0.12:
            scores["grilled chicken"] += 0.18
        if "ice cream" in candidate_pool_set and brightness > 170 and colorfulness > 35:
            scores["ice cream"] += 0.16
        if "banana" in candidate_pool_set and yellow_fraction > 0.16 and brightness > 150:
            scores["banana"] += 0.20
        if "apple" in candidate_pool_set and red_fraction > 0.16 and green_fraction > 0.05:
            scores["apple"] += 0.18
        if cuisine_hint == "South Indian":
            if aspect_ratio > 1.2:
                scores["dosa"] += 0.08
                scores["uttapam"] += 0.05
            if white_fraction > 0.25:
                scores["idli"] += 0.08
                scores["curd rice"] += 0.06
            if yellow_fraction > 0.14:
                scores["lemon rice"] += 0.06
                scores["biryani"] += 0.05

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    filtered_ranked = [(food_name, score) for food_name, score in ranked if score > 0]

    if not filtered_ranked:
        fallback_foods = candidate_pool[:limit] if candidate_pool else ["salad", "rice", "sandwich"]
        return [{"food_name": item, "confidence": 0.25} for item in fallback_foods[:limit]]

    return [
        {
            "food_name": food_name,
            "confidence": round(min(0.95, 0.20 + score), 2),
        }
        for food_name, score in filtered_ranked[:limit]
    ]


def build_food_image_summary(image: Image.Image) -> Dict[str, float]:
    stats = _image_feature_stats(image)
    return {
        "width": float(image.width),
        "height": float(image.height),
        "brightness": round(stats["brightness"], 2),
        "colorfulness": round(stats["colorfulness"], 2),
        "white_fraction": round(stats["white_fraction"], 3),
        "yellow_fraction": round(stats["yellow_fraction"], 3),
        "brown_fraction": round(stats["brown_fraction"], 3),
    }


def analyze_food_image(uploaded_file, cuisine_hint: str = "Auto") -> Dict[str, Any]:
    image = load_image_from_upload(uploaded_file)
    candidates = suggest_food_candidates(getattr(uploaded_file, "name", ""), image=image, cuisine_hint=cuisine_hint)
    auto_detected_food = candidates[0]["food_name"] if candidates else None
    auto_confidence = float(candidates[0]["confidence"]) if candidates else 0.0
    return {
        "image": image,
        "summary": build_food_image_summary(image),
        "candidates": candidates,
        "auto_detected_food": auto_detected_food,
        "auto_confidence": auto_confidence,
        "cuisine_hint": cuisine_hint,
    }


def build_food_recommendation(
    food_name: str,
    portion_size: str,
    predicted_risk: str | None = None,
    bmi: float | None = None,
    blood_sugar: float | None = None,
    diet_score: float | None = None,
    lang: str = "en",
) -> Dict[str, Any]:
    food_info = get_food_info(food_name)
    if not food_info:
        raise ValueError(f"Unknown food item: {food_name}")

    portion_multiplier = PORTION_MULTIPLIERS.get(portion_size, 1.0)
    estimated_calories = round(float(food_info["estimated_calories"]) * portion_multiplier, 2)
    risk_flags = set(food_info.get("risk_flags", []))
    severity_score = 0
    reasons: List[str] = []
    positive_notes: List[str] = []

    if estimated_calories >= 450:
        severity_score += 3
        reasons.append(
            "High-calorie serving for a single meal."
            if lang == "en"
            else "एक ही भोजन के लिए यह उच्च कैलोरी मात्रा है।"
        )
    elif estimated_calories >= 300:
        severity_score += 2
        reasons.append(
            "Calories are on the higher side."
            if lang == "en"
            else "कैलोरी मात्रा अपेक्षाकृत अधिक है।"
        )
    elif estimated_calories <= 150:
        severity_score -= 1
        positive_notes.append(
            "Calorie load is relatively light."
            if lang == "en"
            else "कैलोरी मात्रा अपेक्षाकृत हल्की है।"
        )

    if {"fried", "junk", "processed"}.intersection(risk_flags):
        severity_score += 2
        reasons.append(
            "It is fried / processed / junk-style food."
            if lang == "en"
            else "यह तला हुआ / प्रोसेस्ड / जंक-स्टाइल भोजन है।"
        )

    if "sugary" in risk_flags:
        severity_score += 2
        reasons.append(
            "Sugar content may be high."
            if lang == "en"
            else "इसमें शक्कर की मात्रा अधिक हो सकती है।"
        )

    if {"healthy", "fiber", "protein_rich"}.intersection(risk_flags):
        severity_score -= 2
        positive_notes.append(
            "It has a healthier nutritional profile."
            if lang == "en"
            else "इसका पोषण प्रोफ़ाइल बेहतर माना जा सकता है।"
        )

    if predicted_risk == "High" and estimated_calories >= 250:
        severity_score += 2
        reasons.append(
            "Not ideal for a high-risk health profile."
            if lang == "en"
            else "उच्च स्वास्थ्य जोखिम प्रोफ़ाइल के लिए यह आदर्श नहीं है।"
        )
    elif predicted_risk == "Moderate" and estimated_calories >= 300:
        severity_score += 1
        reasons.append(
            "Moderate-risk users should limit frequent intake."
            if lang == "en"
            else "मध्यम जोखिम वाले उपयोगकर्ताओं को इसे बार-बार लेने से बचना चाहिए।"
        )

    if bmi is not None and bmi >= 25 and estimated_calories >= 300:
        severity_score += 1
        reasons.append(
            "Higher-calorie foods can make weight control harder."
            if lang == "en"
            else "उच्च कैलोरी वाले भोजन वजन नियंत्रण को कठिन बना सकते हैं।"
        )

    if blood_sugar is not None and blood_sugar >= 126 and {"sugary", "refined_carb", "natural_sugar"}.intersection(risk_flags):
        severity_score += 2
        reasons.append(
            "Use caution because blood sugar is elevated."
            if lang == "en"
            else "ब्लड शुगर बढ़ी हुई होने पर सावधानी रखें।"
        )

    if diet_score is not None and diet_score < 50 and {"healthy", "fiber", "protein_rich"}.intersection(risk_flags):
        severity_score -= 1
        positive_notes.append(
            "This can be a better pick than many processed alternatives."
            if lang == "en"
            else "यह कई प्रोसेस्ड विकल्पों की तुलना में बेहतर चुनाव हो सकता है।"
        )

    if severity_score >= 5:
        decision_label = "Better avoid frequently"
    elif severity_score >= 2:
        decision_label = "Consume in moderation"
    else:
        decision_label = "Recommended"

    if not reasons:
        reasons.append(
            "No major nutritional red flag was detected for this portion."
            if lang == "en"
            else "इस मात्रा के लिए कोई बड़ा पोषण-संबंधी चेतावनी संकेत नहीं मिला।"
        )

    primary_reason = reasons[0]
    positive_reason = positive_notes[0] if positive_notes else (
        "A lighter portion may be a smarter choice."
        if lang == "en"
        else "हल्की मात्रा एक बेहतर विकल्प हो सकती है।"
    )

    return {
        "food_name": food_info["food_name"],
        "food_name_display": translate_food_name(food_info["food_name"], lang),
        "serving_size": food_info["serving_size"],
        "portion_size": portion_size,
        "portion_size_display": translate_portion_size(portion_size, lang),
        "estimated_calories": estimated_calories,
        "food_category": food_info["food_category"],
        "decision_label": decision_label,
        "decision_label_display": translate_decision_label(decision_label, lang),
        "primary_reason": primary_reason,
        "positive_reason": positive_reason,
        "healthier_alternative": food_info.get("healthier_alternative"),
        "healthier_alternative_display": translate_food_name(str(food_info.get("healthier_alternative", "")), lang),
        "risk_flags": sorted(risk_flags),
        "severity_score": severity_score,
        "disclaimer": (
            "Calories are approximate and depend on portion size, ingredients, and cooking method."
            if lang == "en"
            else "कैलोरी अनुमानित हैं और मात्रा, सामग्री तथा पकाने के तरीके पर निर्भर करती हैं।"
        ),
    }
