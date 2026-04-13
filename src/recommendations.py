from __future__ import annotations

from typing import Dict, List

from .features import compute_hrs_components
from .translations import translate_risk


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
    lang: str = "en",
) -> List[str]:
    recommendations: List[str] = []

    if lang == "hi":
        if diet_score < 50:
            recommendations.append("फलों, सब्ज़ियों और प्रोटीन को बढ़ाकर तथा जंक फूड कम करके अपने आहार की गुणवत्ता सुधारें।")
        elif diet_score >= 75:
            recommendations.append("अपनी वर्तमान स्वस्थ डाइट आदत को नियमित रूप से बनाए रखें।")

        if sleep_hours < 7:
            recommendations.append("बेहतर रिकवरी और मेटाबोलिक स्वास्थ्य के लिए नींद की अवधि 7-8 घंटे तक बढ़ाएँ।")
        elif sleep_hours > 9:
            recommendations.append("नींद की अवधि को 7-8 घंटे के संतुलित स्तर के आसपास रखने का प्रयास करें।")

        if activity_level < 5:
            recommendations.append("चलना, व्यायाम या खेल जैसी गतिविधियाँ बढ़ाएँ और रोज़ कम से कम 30 मिनट सक्रिय रहें।")
        elif activity_level >= 8:
            recommendations.append("आपकी शारीरिक गतिविधि अच्छी है; इस सक्रिय दिनचर्या को जारी रखें।")

        if bmi >= 30:
            recommendations.append("BMI मोटापे के जोखिम को दर्शाता है। डाइट नियंत्रण और नियमित व्यायाम से वजन प्रबंधन पर ध्यान दें।")
        elif bmi >= 25:
            recommendations.append("BMI सामान्य सीमा से ऊपर है। धीरे-धीरे जीवनशैली में सुधार भविष्य के जोखिम को कम कर सकता है।")
        elif bmi < 18.5:
            recommendations.append("BMI सामान्य से कम है। संतुलित पोषण लें और आवश्यकता हो तो विशेषज्ञ सलाह लें।")

        if blood_pressure_systolic is not None and blood_pressure_diastolic is not None:
            if blood_pressure_systolic >= 140 or blood_pressure_diastolic >= 90:
                recommendations.append("रक्तचाप नियमित रूप से जाँचें, अधिक नमक कम करें और आवश्यकता हो तो चिकित्सकीय समीक्षा कराएँ।")
            elif blood_pressure_systolic >= 130 or blood_pressure_diastolic >= 80:
                recommendations.append("बढ़े हुए रक्तचाप को तनाव नियंत्रण, व्यायाम और बेहतर भोजन विकल्पों से सुधारा जा सकता है।")

        if blood_sugar is not None and blood_sugar >= 126:
            recommendations.append("ब्लड शुगर बढ़ी हुई है। अतिरिक्त चीनी का सेवन कम करें और प्रोफेशनल स्क्रीनिंग पर विचार करें।")

        if smoking_habit == "Current Smoker":
            recommendations.append("धूम्रपान छोड़ना दीर्घकालिक स्वास्थ्य जोखिम कम करने के सबसे प्रभावी तरीकों में से एक है।")

        if screen_time_hours is not None and screen_time_hours >= 8:
            recommendations.append("लंबे स्क्रीन टाइम को कम करें और दिनभर में छोटे-छोटे मूवमेंट ब्रेक शामिल करें।")

        if stress_level is not None:
            if stress_level >= 8:
                recommendations.append("रिलैक्सेशन, ब्रेक, ब्रीदिंग एक्सरसाइज या काउंसलिंग जैसे तनाव प्रबंधन उपाय अपनाएँ।")
            elif stress_level >= 6:
                recommendations.append("मध्यम तनाव को बेहतर दिनचर्या, नींद और शारीरिक गतिविधि से कम किया जा सकता है।")

        if predicted_risk == "High":
            recommendations.append(f"{translate_risk(predicted_risk, lang)} जोखिम भविष्यवाणी प्रारंभिक चिकित्सकीय परामर्श और नियमित निगरानी की आवश्यकता दर्शाती है।")
        elif predicted_risk == "Moderate":
            recommendations.append(f"{translate_risk(predicted_risk, lang)} जोखिम को लगातार जीवनशैली सुधार और फॉलो-अप जाँच से कम किया जा सकता है।")
        else:
            recommendations.append("कम जोखिम उत्साहजनक है। स्वस्थ आदतों को बनाए रखें।")

        if not recommendations:
            recommendations.append("संतुलित जीवनशैली बनाए रखें और नियमित स्वास्थ्य निगरानी करते रहें।")
    else:
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


def generate_explainability_text(diet_score: float, sleep_hours: float, activity_level: float, bmi: float, lang: str = "en") -> str:
    components: Dict[str, float] = compute_hrs_components(diet_score, sleep_hours, activity_level, bmi)
    risk_parts_en = {
        "poor diet": components["diet_risk"],
        "sleep imbalance": components["sleep_risk"],
        "low physical activity": components["activity_risk"],
        "BMI deviation": components["bmi_risk"],
    }

    if lang == "hi":
        translated_parts = {
            "poor diet": "खराब आहार",
            "sleep imbalance": "अनियमित नींद",
            "low physical activity": "कम शारीरिक गतिविधि",
            "BMI deviation": "BMI में विचलन",
        }
        sorted_parts = sorted(risk_parts_en.items(), key=lambda item: item[1], reverse=True)
        top_negative = [translated_parts[name] for name, score in sorted_parts[:2] if score > 0.35]
        positive_parts = [translated_parts[name] for name, score in sorted_parts if score < 0.2]

        if top_negative:
            primary = " और ".join(top_negative)
            message = f"जो मुख्य कारक जोखिम बढ़ा रहे हैं वे हैं: {primary}।"
        else:
            message = "कोई एकल कारक जोखिम को बहुत अधिक नहीं बढ़ा रहा है; कुल संतुलन उचित दिखता है।"

        if positive_parts:
            message += f" सहायक कारक: {', '.join(positive_parts[:2])}।"

        if bmi >= 30 and sleep_hours < 6.5:
            message += " उच्च BMI और कम नींद मिलकर स्वास्थ्य जोखिम को काफी बढ़ा सकते हैं।"
        elif diet_score >= 75 and activity_level >= 7:
            message += " अच्छा आहार और बेहतर गतिविधि स्तर जोखिम कम करने में मदद कर रहे हैं।"
        return message

    sorted_parts = sorted(risk_parts_en.items(), key=lambda item: item[1], reverse=True)
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
