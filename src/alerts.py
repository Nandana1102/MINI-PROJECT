from __future__ import annotations

from typing import List, Tuple

from .translations import translate_risk


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
    lang: str = "en",
) -> List[AlertItem]:
    alerts: List[AlertItem] = []

    if lang == "hi":
        if bmi >= 30:
            alerts.append(("error", "आपका BMI मोटापे की श्रेणी में है। वजन नियंत्रण और जीवनशैली में सुधार की सख्त सलाह दी जाती है।"))
        elif bmi >= 25:
            alerts.append(("warning", "आपका BMI अधिक वज़न की श्रेणी में है। धीरे-धीरे सुधार करने से दीर्घकालिक स्वास्थ्य जोखिम कम हो सकता है।"))
        elif bmi < 18.5:
            alerts.append(("warning", "आपका BMI कम वज़न की श्रेणी में है। पोषण संतुलन की समीक्षा की जानी चाहिए।"))

        if sleep_hours < 5.5:
            alerts.append(("error", "नींद बहुत कम है। बहुत कम नींद थकान, मेटाबोलिक तनाव और कुल स्वास्थ्य जोखिम बढ़ा सकती है।"))
        elif sleep_hours < 7:
            alerts.append(("warning", "नींद अनुशंसित सीमा से कम है। लगभग 7 से 8 घंटे का लक्ष्य रखें।"))
        elif sleep_hours > 9.5:
            alerts.append(("warning", "नींद की अवधि असामान्य रूप से अधिक है। नींद की गुणवत्ता या अनियमित दिनचर्या की जाँच करें।"))

        if blood_pressure_systolic is not None and blood_pressure_diastolic is not None:
            if blood_pressure_systolic >= 140 or blood_pressure_diastolic >= 90:
                alerts.append(("error", "रक्तचाप उच्च सीमा में है। नियमित निगरानी और चिकित्सकीय सलाह आवश्यक है।"))
            elif blood_pressure_systolic >= 130 or blood_pressure_diastolic >= 80:
                alerts.append(("warning", "रक्तचाप बढ़ा हुआ है और इसे सावधानी से मॉनिटर किया जाना चाहिए।"))

        if blood_sugar is not None:
            if blood_sugar >= 200:
                alerts.append(("error", "ब्लड शुगर बहुत अधिक है। तुरंत निगरानी और विशेषज्ञ परामर्श की सलाह दी जाती है।"))
            elif blood_sugar >= 126:
                alerts.append(("warning", "ब्लड शुगर बढ़ी हुई लग रही है और उचित जाँच की जानी चाहिए।"))

        if smoking_habit == "Current Smoker":
            alerts.append(("error", "धूम्रपान एक प्रमुख स्वास्थ्य जोखिम कारक है और दीर्घकालिक परिणामों को खराब कर सकता है।"))
        elif smoking_habit == "Former Smoker":
            alerts.append(("info", "पूर्व धूम्रपान का इतिहास दीर्घकालिक स्वास्थ्य निगरानी में ध्यान में रखा जाना चाहिए।"))

        if screen_time_hours is not None and screen_time_hours >= 8:
            alerts.append(("warning", "स्क्रीन टाइम अधिक है और यह निष्क्रिय जीवनशैली का संकेत हो सकता है। नियमित मूवमेंट ब्रेक लें।"))

        if stress_level is not None:
            if stress_level >= 8:
                alerts.append(("error", "तनाव स्तर बहुत अधिक है। तनाव प्रबंधन और रिकवरी रणनीतियाँ महत्वपूर्ण हैं।"))
            elif stress_level >= 6:
                alerts.append(("warning", "तनाव स्तर मध्यम से अधिक है। रिलैक्सेशन, बेहतर नींद और कार्य-संतुलन सहायक हो सकते हैं।"))

        if predicted_risk == "High":
            alerts.append(("error", f"कुल अनुमानित स्वास्थ्य जोखिम {translate_risk(predicted_risk, lang)} है। प्रारंभिक हस्तक्षेप और फॉलो-अप की सलाह दी जाती है।"))
        elif predicted_risk == "Moderate":
            alerts.append(("warning", f"कुल अनुमानित स्वास्थ्य जोखिम {translate_risk(predicted_risk, lang)} है। जीवनशैली में सुधार भविष्य के जोखिम को कम कर सकता है।"))

        if not alerts:
            alerts.append(("success", "वर्तमान इनपुट के आधार पर कोई बड़ा तत्काल अलर्ट नहीं पाया गया।"))
        return alerts

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
        alerts.append(("error", f"Overall predicted health risk is {translate_risk(predicted_risk, lang)}. Early intervention and follow-up are recommended."))
    elif predicted_risk == "Moderate":
        alerts.append(("warning", f"Overall predicted health risk is {translate_risk(predicted_risk, lang)}. Improvement in lifestyle factors can reduce future risk."))

    if not alerts:
        alerts.append(("success", "No major immediate alert was detected from the current inputs."))

    return alerts
