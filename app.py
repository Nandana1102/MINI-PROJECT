from __future__ import annotations

import pandas as pd
import streamlit as st

from src.alerts import generate_health_alerts
from src.features import build_user_feature_dict, compute_hrs_components
from src.history import append_prediction_history, load_prediction_history
from src.modeling import (
    build_confusion_matrix_figure,
    build_feature_importance_figure,
    build_model_comparison_figure,
    load_bundle,
    predict_single,
    train_and_save,
)
from src.pdf_reporting import build_pdf_report_bytes
from src.recommendations import generate_explainability_text, generate_recommendations
from src.reporting import build_text_report
from src.utils import FEATURE_COLUMNS, model_bundle_path, risk_color
from src.wellness_tools import calculate_bmi, calculate_diet_score, calorie_guidance_text, estimate_daily_calories


st.set_page_config(page_title="Health Risk Assessment Dashboard", page_icon="🩺", layout="wide")


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background-image:
                linear-gradient(rgba(6, 24, 38, 0.60), rgba(6, 24, 38, 0.60)),
                url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjAwIDkwMCI+CiAgPGRlZnM+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzA2MTgyNiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjUwJSIgc3RvcC1jb2xvcj0iIzBiMmY0NSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxMDNhNTIiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIxNjAwIiBoZWlnaHQ9IjkwMCIgZmlsbD0idXJsKCNnKSIvPgogIDxjaXJjbGUgY3g9IjIyMCIgY3k9IjE4MCIgcj0iMTgwIiBmaWxsPSIjMzhiZGY4IiBvcGFjaXR5PSIwLjA4Ii8+CiAgPGNpcmNsZSBjeD0iMTMyMCIgY3k9IjE2MCIgcj0iMTQwIiBmaWxsPSIjMjJjNTVlIiBvcGFjaXR5PSIwLjA4Ii8+CiAgPGNpcmNsZSBjeD0iMTM4MCIgY3k9IjcyMCIgcj0iMjIwIiBmaWxsPSIjMjU2M2ViIiBvcGFjaXR5PSIwLjA4Ii8+CiAgPHBhdGggZD0iTTAgNTIwIEMxODAgNDcwLCAyNjAgNTYwLCAzODAgNTIwIFM2MjAgNDcwLCA3NDAgNTIwIFM5ODAgNTYwLCAxMTAwIDUyMCBTMTM0MCA0NzAsIDE2MDAgNTIwIiBzdHJva2U9IiM5M2M1ZmQiIHN0cm9rZS1vcGFjaXR5PSIwLjEyIiBzdHJva2Utd2lkdGg9IjgiIGZpbGw9Im5vbmUiLz4KICA8cGF0aCBkPSJNMTIwIDYxMCBINDIwIEw0NzAgNjEwIEw1MTUgNTIwIEw1NjAgNzAwIEw2MjAgNDMwIEw2ODAgNjEwIEgxNDgwIiBzdHJva2U9IiM2N2U4ZjkiIHN0cm9rZS1vcGFjaXR5PSIwLjIwIiBzdHJva2Utd2lkdGg9IjYiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogIDxnIG9wYWNpdHk9IjAuMTIiIGZpbGw9IiNlMGYyZmUiPgogICAgPHJlY3QgeD0iMTE4MCIgeT0iMjgwIiB3aWR0aD0iMjQiIGhlaWdodD0iOTAiIHJ4PSI0Ii8+CiAgICA8cmVjdCB4PSIxMTQ3IiB5PSIzMTMiIHdpZHRoPSI5MCIgaGVpZ2h0PSIyNCIgcng9IjQiLz4KICAgIDxyZWN0IHg9IjI5MCIgeT0iMzAwIiB3aWR0aD0iMjAiIGhlaWdodD0iNzYiIHJ4PSI0Ii8+CiAgICA8cmVjdCB4PSIyNjIiIHk9IjMyOCIgd2lkdGg9Ijc2IiBoZWlnaHQ9IjIwIiByeD0iNCIvPgogIDwvZz4KPC9zdmc+");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .main .block-container {
            background: rgba(255, 255, 255, 0.92);
            padding: 1.4rem 1.4rem 1.2rem 1.4rem;
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8, 34, 53, 0.96) 0%, rgba(14, 58, 83, 0.96) 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_model_bundle():
    if not model_bundle_path().exists():
        return train_and_save(n_samples=1000, random_state=42)
    return load_bundle()


def format_optional(value, suffix: str = "") -> str:
    if value is None or value == "":
        return "Not provided"
    return f"{value}{suffix}"


inject_custom_css()
bundle = get_model_bundle()

st.title("🩺 Explainable Health Risk Assessment Dashboard")
st.markdown(
    "A smart healthcare mini project with **ML prediction, diet scoring, calorie estimation, health alerts, history tracking, PDF reporting, and what-if simulation**."
)

st.sidebar.header("Dashboard Controls")
st.sidebar.info(
    "The ML model uses core lifestyle factors. Optional advanced health parameters are used for alerts, recommendations, reporting, and history analysis."
)
model_name = st.sidebar.selectbox("Prediction Model", ["Random Forest", "Logistic Regression"], index=0)
diet_input_mode = st.sidebar.radio("Diet Input Mode", ["Calculate Diet Score", "Manual Diet Score"], index=0)
bmi_input_mode = st.sidebar.radio("BMI Input Mode", ["Calculate BMI from Height & Weight", "Manual BMI"], index=0)
include_advanced = st.sidebar.checkbox("Include advanced health parameters", value=False)

summary_cols = st.columns(3)
summary_cols[0].info("**Core Prediction Inputs**\n\nDiet score, sleep, activity, BMI, and engineered HRS.")
summary_cols[1].info("**Optional Advanced Inputs**\n\nBlood pressure, blood sugar, smoking, screen time, and stress.")
summary_cols[2].info("**Smart Outputs**\n\nRisk category, alerts, recommendations, history trends, and PDF report.")

st.info("**Practical design:** Users can do a **Basic Assessment** with common inputs only, or enable **Advanced Assessment** when clinical and behavioral values are available.")

left_col, right_col = st.columns([1.45, 1])

with left_col:
    st.subheader("1) User Input Section")

    basic_col1, basic_col2 = st.columns(2)
    with basic_col1:
        age = st.number_input("Age", min_value=15, max_value=90, value=21)
        gender = st.selectbox("Gender", ["Female", "Male"])
        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=160.0, step=0.5)
    with basic_col2:
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=180.0, value=60.0, step=0.5)
        calorie_activity = st.selectbox(
            "Daily Activity Type for Calorie Estimation",
            ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"],
            index=2,
        )

    st.markdown("### Diet Assessment")
    if diet_input_mode == "Calculate Diet Score":
        diet_col1, diet_col2 = st.columns(2)
        with diet_col1:
            fruits_veg_servings = st.slider("Fruits / Vegetables Servings per Day", 0, 8, 3)
            water_liters_per_day = st.slider("Water Intake per Day (Liters)", 0.0, 5.0, 2.0, 0.1)
            breakfast_days_per_week = st.slider("Breakfast Days per Week", 0, 7, 5)
        with diet_col2:
            protein_days_per_week = st.slider("Protein-Rich Meals Days per Week", 0, 7, 4)
            junk_food_meals_per_week = st.slider("Junk Food Meals per Week", 0, 14, 3)
            sugary_drinks_per_week = st.slider("Sugary Drinks per Week", 0, 14, 3)

        diet_result = calculate_diet_score(
            fruits_veg_servings=fruits_veg_servings,
            junk_food_meals_per_week=junk_food_meals_per_week,
            sugary_drinks_per_week=sugary_drinks_per_week,
            water_liters_per_day=water_liters_per_day,
            breakfast_days_per_week=breakfast_days_per_week,
            protein_days_per_week=protein_days_per_week,
        )
        diet_score = float(diet_result["diet_score"])
        st.success(f"Calculated Diet Score: {diet_score:.2f} / 100")
    else:
        diet_score = float(st.slider("Diet Score", 0, 100, 60, help="Higher score means healthier dietary habits."))
        diet_result = None

    st.markdown("### Core Lifestyle Inputs")
    lifestyle_col1, lifestyle_col2 = st.columns(2)
    with lifestyle_col1:
        sleep_hours = st.slider("Sleep Hours", 3.0, 10.0, 7.0, 0.1)
    with lifestyle_col2:
        activity_level = st.slider("Physical Activity Level", 0.0, 10.0, 5.0, 0.1, help="0 = sedentary, 10 = highly active")

    st.markdown("### BMI and Calorie Estimation")
    calculated_bmi = calculate_bmi(weight_kg=weight_kg, height_cm=height_cm)
    if bmi_input_mode == "Calculate BMI from Height & Weight":
        bmi = float(calculated_bmi)
        st.success(f"Calculated BMI from height and weight: {bmi:.2f}")
    else:
        bmi = float(st.slider("Manual BMI", 15.0, 40.0, float(calculated_bmi), 0.1))
        st.caption(f"Reference BMI from height and weight: {calculated_bmi:.2f}")

    calorie_profile = estimate_daily_calories(
        age=int(age),
        gender=gender,
        height_cm=float(height_cm),
        weight_kg=float(weight_kg),
        activity_level=calorie_activity,
    )

    advanced_values: dict[str, object] = {
        "smoking_habit": None,
        "screen_time_hours": None,
        "stress_level": None,
        "blood_pressure_systolic": None,
        "blood_pressure_diastolic": None,
        "blood_sugar": None,
    }

    if include_advanced:
        st.markdown("### Advanced Optional Health Inputs")
        st.caption("Enable these only if the user knows the values. They improve alerts and reporting, not the core trained ML model.")
        adv_col1, adv_col2 = st.columns(2)
        with adv_col1:
            advanced_values["screen_time_hours"] = float(st.slider("Screen Time per Day (Hours)", 0.0, 16.0, 6.0, 0.5))
            advanced_values["stress_level"] = int(st.slider("Stress Level", 0, 10, 5))
            advanced_values["smoking_habit"] = st.selectbox("Smoking Habit", ["Non-Smoker", "Former Smoker", "Current Smoker"])
        with adv_col2:
            advanced_values["blood_pressure_systolic"] = int(st.number_input("Blood Pressure Systolic (mmHg)", min_value=80, max_value=220, value=120))
            advanced_values["blood_pressure_diastolic"] = int(st.number_input("Blood Pressure Diastolic (mmHg)", min_value=50, max_value=140, value=80))
            advanced_values["blood_sugar"] = float(st.number_input("Blood Sugar (mg/dL)", min_value=60.0, max_value=350.0, value=100.0, step=1.0))
    else:
        st.info("Advanced health parameters are optional and currently not included.")

    if st.button("Predict Health Risk", type="primary", use_container_width=True):
        st.session_state["run_prediction"] = True
        st.session_state["save_history_now"] = True
        st.session_state["input_values"] = {
            "diet_score": float(diet_score),
            "sleep_hours": float(sleep_hours),
            "activity_level": float(activity_level),
            "bmi": float(bmi),
        }
        st.session_state["context_values"] = {
            "age": int(age),
            "gender": gender,
            "height_cm": float(height_cm),
            "weight_kg": float(weight_kg),
            "calorie_activity": calorie_activity,
            "include_advanced": include_advanced,
            **advanced_values,
        }
        st.session_state["diet_result"] = diet_result
        st.session_state["calorie_profile"] = calorie_profile
        st.session_state["calorie_summary"] = calorie_guidance_text(calorie_profile)

with right_col:
    st.subheader("2) System Overview")
    st.markdown(
        """
- Predicts **Low / Moderate / High** health risk.
- Computes a rule-based **Health Risk Score (HRS)**.
- Compares **Logistic Regression** and **Random Forest**.
- Supports **Basic Assessment** and **Advanced Assessment** modes.
- Adds **diet score calculation**, **BMI auto-calculation**, and **calorie estimation**.
- Uses **health alerts**, **history tracking**, **what-if simulation**, and **PDF download**.
        """
    )
    st.info(
        "Core ML prediction uses Diet Score, Sleep Hours, Physical Activity Level, BMI, and engineered HRS. Optional advanced values enrich alerts, recommendations, and reporting."
    )
    st.success(
        f"Current Input Mode\n\nDiet: {diet_input_mode}\nBMI: {bmi_input_mode}\nAdvanced Parameters: {'Enabled' if include_advanced else 'Disabled'}"
    )

if st.session_state.get("run_prediction"):
    values = st.session_state["input_values"]
    context = st.session_state.get("context_values", {})
    include_advanced = bool(context.get("include_advanced", False))
    user_data = build_user_feature_dict(**values)
    input_df = pd.DataFrame([{feature: user_data[feature] for feature in FEATURE_COLUMNS}])
    predicted_risk, probabilities = predict_single(bundle, input_df, model_name)
    explanation = generate_explainability_text(**values)

    recommendations = generate_recommendations(
        predicted_risk=predicted_risk,
        blood_pressure_systolic=context.get("blood_pressure_systolic") if include_advanced else None,
        blood_pressure_diastolic=context.get("blood_pressure_diastolic") if include_advanced else None,
        blood_sugar=context.get("blood_sugar") if include_advanced else None,
        smoking_habit=context.get("smoking_habit") if include_advanced else None,
        screen_time_hours=context.get("screen_time_hours") if include_advanced else None,
        stress_level=context.get("stress_level") if include_advanced else None,
        **values,
    )

    alerts = generate_health_alerts(
        sleep_hours=values["sleep_hours"],
        bmi=values["bmi"],
        predicted_risk=predicted_risk,
        blood_pressure_systolic=context.get("blood_pressure_systolic") if include_advanced else None,
        blood_pressure_diastolic=context.get("blood_pressure_diastolic") if include_advanced else None,
        blood_sugar=context.get("blood_sugar") if include_advanced else None,
        smoking_habit=context.get("smoking_habit") if include_advanced else None,
        screen_time_hours=context.get("screen_time_hours") if include_advanced else None,
        stress_level=context.get("stress_level") if include_advanced else None,
    )

    diet_result = st.session_state.get("diet_result")
    calorie_profile = st.session_state.get("calorie_profile")
    calorie_summary = st.session_state.get("calorie_summary")

    component_data = compute_hrs_components(**values)
    contribution_df = pd.DataFrame(
        {
            "Risk Component": ["Diet Risk", "Sleep Risk", "Activity Risk", "BMI Risk"],
            "Contribution": [
                round(0.25 * component_data["diet_risk"] * 100, 2),
                round(0.20 * component_data["sleep_risk"] * 100, 2),
                round(0.20 * component_data["activity_risk"] * 100, 2),
                round(0.35 * component_data["bmi_risk"] * 100, 2),
            ],
        }
    )

    additional_context_lines = [
        f"- Age: {context.get('age')}",
        f"- Gender: {context.get('gender')}",
        f"- Height (cm): {context.get('height_cm')}",
        f"- Weight (kg): {context.get('weight_kg')}",
        f"- Advanced Parameters Included: {'Yes' if include_advanced else 'No'}",
    ]
    if include_advanced:
        additional_context_lines.extend(
            [
                f"- Blood Pressure: {format_optional(context.get('blood_pressure_systolic'))}/{format_optional(context.get('blood_pressure_diastolic'))} mmHg",
                f"- Blood Sugar: {format_optional(context.get('blood_sugar'), ' mg/dL')}",
                f"- Smoking Habit: {format_optional(context.get('smoking_habit'))}",
                f"- Screen Time: {format_optional(context.get('screen_time_hours'), ' hours/day')}",
                f"- Stress Level: {format_optional(context.get('stress_level'), ' / 10')}",
            ]
        )

    alert_text = "\n".join(f"- {message}" for _, message in alerts)
    additional_sections = [
        ("ADDITIONAL HEALTH CONTEXT", "\n".join(additional_context_lines)),
        ("HEALTH ALERTS", alert_text),
        ("CALORIE GUIDANCE", calorie_summary),
        (
            "HRS CONTRIBUTION BREAKDOWN",
            "\n".join(
                [
                    f"- Diet Risk Contribution: {contribution_df.iloc[0]['Contribution']}",
                    f"- Sleep Risk Contribution: {contribution_df.iloc[1]['Contribution']}",
                    f"- Activity Risk Contribution: {contribution_df.iloc[2]['Contribution']}",
                    f"- BMI Risk Contribution: {contribution_df.iloc[3]['Contribution']}",
                ]
            ),
        ),
    ]
    if diet_result:
        additional_sections.append(
            (
                "DIET SCORE BREAKDOWN",
                "\n".join(
                    [
                        f"- Diet Score: {diet_result['diet_score']}",
                        f"- Fruits & Vegetables Score: {diet_result['fruits_veg_score']}",
                        f"- Water Intake Score: {diet_result['water_score']}",
                        f"- Breakfast Score: {diet_result['breakfast_score']}",
                        f"- Protein Intake Score: {diet_result['protein_score']}",
                        f"- Junk Food Penalty: {diet_result['junk_food_penalty']}",
                        f"- Sugary Drinks Penalty: {diet_result['sugary_drinks_penalty']}",
                    ]
                ),
            )
        )

    report_text = build_text_report(
        diet_score=user_data["diet_score"],
        sleep_hours=user_data["sleep_hours"],
        activity_level=user_data["activity_level"],
        bmi=user_data["bmi"],
        bmi_category=user_data["bmi_category"],
        hrs_score=user_data["hrs_score"],
        predicted_risk=predicted_risk,
        model_name=model_name,
        explainability_text=explanation,
        recommendations=recommendations,
        additional_sections=additional_sections,
    )

    pdf_input_rows = [
        ("Age", str(context.get("age"))),
        ("Gender", str(context.get("gender"))),
        ("Height (cm)", str(context.get("height_cm"))),
        ("Weight (kg)", str(context.get("weight_kg"))),
        ("Diet Score", f"{user_data['diet_score']:.2f}"),
        ("Sleep Hours", f"{user_data['sleep_hours']:.2f}"),
        ("Physical Activity Level", f"{user_data['activity_level']:.2f}"),
        ("BMI", f"{user_data['bmi']:.2f}"),
        ("BMI Category", str(user_data["bmi_category"])),
        ("Advanced Parameters Included", "Yes" if include_advanced else "No"),
        ("Blood Pressure", f"{format_optional(context.get('blood_pressure_systolic'))}/{format_optional(context.get('blood_pressure_diastolic'))} mmHg" if include_advanced else "Not provided"),
        ("Blood Sugar", format_optional(context.get("blood_sugar"), " mg/dL") if include_advanced else "Not provided"),
        ("Smoking Habit", format_optional(context.get("smoking_habit")) if include_advanced else "Not provided"),
        ("Screen Time", format_optional(context.get("screen_time_hours"), " hours/day") if include_advanced else "Not provided"),
        ("Stress Level", format_optional(context.get("stress_level"), " / 10") if include_advanced else "Not provided"),
    ]
    pdf_output_rows = [
        ("Health Risk Score (HRS)", f"{user_data['hrs_score']:.2f}"),
        ("Predicted Risk", predicted_risk),
        ("Selected Model", model_name),
        ("Explainability Summary", explanation),
        ("Calorie Guidance", calorie_summary),
    ]
    pdf_bytes = build_pdf_report_bytes(
        input_rows=pdf_input_rows,
        output_rows=pdf_output_rows,
        recommendations=recommendations,
        alerts=[message for _, message in alerts],
        additional_sections=additional_sections,
    )

    if st.session_state.get("save_history_now"):
        append_prediction_history(
            {
                "model_name": model_name,
                "age": context.get("age"),
                "gender": context.get("gender"),
                "diet_score": round(user_data["diet_score"], 2),
                "sleep_hours": round(user_data["sleep_hours"], 2),
                "activity_level": round(user_data["activity_level"], 2),
                "bmi": round(user_data["bmi"], 2),
                "bmi_category": user_data["bmi_category"],
                "hrs_score": round(user_data["hrs_score"], 2),
                "predicted_risk": predicted_risk,
                "advanced_parameters_used": include_advanced,
                "blood_pressure_systolic": context.get("blood_pressure_systolic") if include_advanced else None,
                "blood_pressure_diastolic": context.get("blood_pressure_diastolic") if include_advanced else None,
                "blood_sugar": context.get("blood_sugar") if include_advanced else None,
                "smoking_habit": context.get("smoking_habit") if include_advanced else None,
                "screen_time_hours": context.get("screen_time_hours") if include_advanced else None,
                "stress_level": context.get("stress_level") if include_advanced else None,
            }
        )
        st.session_state["save_history_now"] = False

    history_df = load_prediction_history()

    st.markdown("---")
    st.subheader("Prediction Result")
    metric_cols = st.columns(4)
    metric_cols[0].metric("HRS Score", f"{user_data['hrs_score']:.2f}")
    metric_cols[1].metric("Predicted Risk", predicted_risk)
    metric_cols[2].metric("BMI Category", user_data["bmi_category"])
    metric_cols[3].metric("Selected Model", model_name)

    st.markdown(
        f"<div style='padding:14px;border-radius:14px;background-color:{risk_color(predicted_risk)};color:white;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,0.10);'>Predicted Health Risk Category: {predicted_risk}</div>",
        unsafe_allow_html=True,
    )

    prob_df = pd.DataFrame({"Risk Category": bundle["label_classes"], "Probability": probabilities})
    st.bar_chart(prob_df.set_index("Risk Category"))

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "Explanation",
            "Recommendations",
            "Diet & Calories",
            "Alerts & History",
            "What-If Simulation",
            "Model Evaluation",
            "Download Reports",
        ]
    )

    with tab1:
        st.write(explanation)
        st.caption("This XAI summary is derived from the strongest input-based risk components.")
        st.markdown("**HRS Contribution Breakdown**")
        st.bar_chart(contribution_df.set_index("Risk Component"))

    with tab2:
        for item in recommendations:
            st.write(f"- {item}")

    with tab3:
        if diet_result:
            st.markdown("**Diet Score Breakdown**")
            st.write(
                {
                    "Diet Score": diet_result["diet_score"],
                    "Fruits & Vegetables Score": diet_result["fruits_veg_score"],
                    "Water Intake Score": diet_result["water_score"],
                    "Breakfast Score": diet_result["breakfast_score"],
                    "Protein Intake Score": diet_result["protein_score"],
                    "Junk Food Penalty": diet_result["junk_food_penalty"],
                    "Sugary Drinks Penalty": diet_result["sugary_drinks_penalty"],
                }
            )
        else:
            st.info("Diet score was entered manually for this prediction.")

        cal_cols = st.columns(3)
        cal_cols[0].metric("BMR", f"{calorie_profile['bmr']} kcal/day")
        cal_cols[1].metric("Maintenance Calories", f"{calorie_profile['maintenance_calories']} kcal/day")
        cal_cols[2].metric("Weight Loss Target", f"{calorie_profile['weight_loss_target']} kcal/day")
        st.write(calorie_summary)

    with tab4:
        st.markdown("**Health Alerts**")
        for severity, message in alerts:
            if severity == "error":
                st.error(message)
            elif severity == "warning":
                st.warning(message)
            elif severity == "success":
                st.success(message)
            else:
                st.info(message)

        st.markdown("**User Prediction History**")
        if history_df.empty:
            st.info("No saved history yet. Run a prediction to create history entries.")
        else:
            history_display = history_df.copy()
            if "timestamp" in history_display.columns:
                history_display["timestamp"] = history_display["timestamp"].astype(str)
            st.dataframe(history_display.tail(10), use_container_width=True)

            trend_df = history_df.dropna(subset=["timestamp"]).copy()
            if not trend_df.empty:
                trend_df = trend_df.set_index("timestamp")
                st.markdown("**HRS Trend Over Time**")
                st.line_chart(trend_df[["hrs_score"]])
                st.markdown("**BMI Trend Over Time**")
                st.line_chart(trend_df[["bmi"]])

            if "predicted_risk" in history_df.columns:
                risk_count_df = history_df["predicted_risk"].value_counts().rename_axis("Risk").reset_index(name="Count")
                st.markdown("**Saved Risk Category Distribution**")
                st.bar_chart(risk_count_df.set_index("Risk"))

    with tab5:
        st.markdown("**Try an Improved Scenario and Compare the Prediction**")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            sim_diet = st.slider("Scenario Diet Score", 0, 100, int(round(values["diet_score"])), key="sim_diet")
            sim_sleep = st.slider("Scenario Sleep Hours", 3.0, 10.0, float(values["sleep_hours"]), 0.1, key="sim_sleep")
        with sim_col2:
            sim_activity = st.slider("Scenario Activity Level", 0.0, 10.0, float(values["activity_level"]), 0.1, key="sim_activity")
            sim_bmi = st.slider("Scenario BMI", 15.0, 40.0, float(values["bmi"]), 0.1, key="sim_bmi")

        scenario_values = {
            "diet_score": float(sim_diet),
            "sleep_hours": float(sim_sleep),
            "activity_level": float(sim_activity),
            "bmi": float(sim_bmi),
        }
        scenario_user_data = build_user_feature_dict(**scenario_values)
        scenario_df = pd.DataFrame([{feature: scenario_user_data[feature] for feature in FEATURE_COLUMNS}])
        scenario_risk, scenario_probabilities = predict_single(bundle, scenario_df, model_name)

        compare_cols = st.columns(2)
        with compare_cols[0]:
            st.markdown("**Current Prediction**")
            st.write({"HRS": user_data["hrs_score"], "Predicted Risk": predicted_risk, "BMI Category": user_data["bmi_category"]})
        with compare_cols[1]:
            st.markdown("**Scenario Prediction**")
            st.write({"HRS": scenario_user_data["hrs_score"], "Predicted Risk": scenario_risk, "BMI Category": scenario_user_data["bmi_category"]})

        hrs_delta = round(scenario_user_data["hrs_score"] - user_data["hrs_score"], 2)
        if hrs_delta < 0:
            st.success(f"Scenario improved the HRS by {abs(hrs_delta)} points.")
        elif hrs_delta > 0:
            st.warning(f"Scenario increased the HRS by {hrs_delta} points.")
        else:
            st.info("Scenario HRS is unchanged.")

        scenario_prob_df = pd.DataFrame({"Risk Category": bundle["label_classes"], "Scenario Probability": scenario_probabilities})
        st.bar_chart(scenario_prob_df.set_index("Risk Category"))

    with tab6:
        st.pyplot(build_model_comparison_figure(bundle["metrics"]))
        eval_cols = st.columns(2)
        for idx, eval_model_name in enumerate(["Logistic Regression", "Random Forest"]):
            with eval_cols[idx]:
                st.markdown(f"**{eval_model_name} Metrics**")
                model_metrics = bundle["metrics"][eval_model_name]
                st.write(
                    {
                        "Accuracy": model_metrics["accuracy"],
                        "Precision": model_metrics["precision"],
                        "Recall": model_metrics["recall"],
                        "F1-Score": model_metrics["f1_score"],
                    }
                )
                st.pyplot(
                    build_confusion_matrix_figure(
                        model_metrics["confusion_matrix"],
                        bundle["label_classes"],
                        f"{eval_model_name} Confusion Matrix",
                    )
                )
        st.pyplot(build_feature_importance_figure(bundle["feature_importances"]))

    with tab7:
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="health_risk_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.download_button(
            label="Download Text Report",
            data=report_text,
            file_name="health_risk_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.text_area("Text Report Preview", report_text, height=360)
else:
    st.info("Enter the values and click 'Predict Health Risk' to view the result.")

st.markdown("---")
st.subheader("Dataset Preview")
st.dataframe(bundle["dataset_preview"], use_container_width=True)
