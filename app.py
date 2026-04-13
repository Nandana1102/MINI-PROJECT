from __future__ import annotations

import json
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from src.api_client import (
    ApiClientError,
    get_admin_predictions,
    get_admin_stats,
    get_admin_users,
    get_current_user,
    get_history,
    health_check,
    login_user,
    predict as api_predict,
    register_user,
    update_language_preference,
)
from src.alerts import generate_health_alerts
from src.features import build_user_feature_dict, compute_hrs_components
from src.food_checker import (
    analyze_food_image,
    build_food_recommendation,
    get_ordered_food_options,
    list_cuisine_hints,
    translate_cuisine_hint,
    translate_food_name,
    translate_portion_size,
)
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
from src.translations import (
    t,
    translate_activity_type,
    translate_admin_view_mode,
    translate_bmi_category,
    translate_bmi_input_mode,
    translate_column_name,
    translate_diet_input_mode,
    translate_gender,
    translate_language_name,
    translate_model_name,
    translate_risk,
    translate_risk_component,
    translate_role,
    translate_smoking_habit,
    yes_no,
)
from src.utils import FEATURE_COLUMNS, model_bundle_path, risk_color
from src.wellness_tools import calculate_bmi, calculate_diet_score, calorie_guidance_text, estimate_daily_calories


st.set_page_config(page_title="Health Risk Assessment Dashboard | स्वास्थ्य जोखिम आकलन", page_icon="🩺", layout="wide")


MODEL_OPTIONS = ["Random Forest", "Logistic Regression"]
DIET_INPUT_OPTIONS = ["Calculate Diet Score", "Manual Diet Score"]
BMI_INPUT_OPTIONS = ["Calculate BMI from Height & Weight", "Manual BMI"]
GENDER_OPTIONS = ["Female", "Male"]
CALORIE_ACTIVITY_OPTIONS = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
SMOKING_OPTIONS = ["Non-Smoker", "Former Smoker", "Current Smoker"]
ADMIN_VIEW_OPTIONS = ["Admin Dashboard", "User Dashboard"]
LANGUAGE_OPTIONS = ["en", "hi"]


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
            background: rgba(255, 255, 255, 0.93);
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


def init_session_state() -> None:
    defaults = {
        "api_token": None,
        "api_user": None,
        "api_mode": False,
        "run_prediction": False,
        "prediction_source": "local",
        "language": "en",
        "language_synced_user_id": None,
        "prediction_request": None,
        "prediction_cache_key": None,
        "prediction_base_result": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    return value == ""


def normalize_language_code(value: Any) -> str:
    value_text = str(value or "en").strip().lower()
    return value_text if value_text in LANGUAGE_OPTIONS else "en"


def sync_language_from_api_user() -> None:
    api_user = st.session_state.get("api_user") or {}
    user_id = api_user.get("id")
    if not user_id:
        return

    if st.session_state.get("language_synced_user_id") != user_id:
        st.session_state["language"] = normalize_language_code(api_user.get("preferred_language", "en"))
        st.session_state["language_synced_user_id"] = user_id


def format_optional(value: Any, suffix: str = "", lang: str = "en") -> str:
    if is_missing(value):
        return t("not_provided", lang)
    return f"{value}{suffix}"


def translate_display_value(column: str, value: Any, lang: str) -> Any:
    if is_missing(value):
        return value
    if column == "gender":
        return translate_gender(value, lang)
    if column == "bmi_category":
        return translate_bmi_category(value, lang)
    if column == "predicted_risk":
        return translate_risk(value, lang)
    if column == "smoking_habit":
        return translate_smoking_habit(value, lang)
    if column == "model_name":
        return translate_model_name(value, lang)
    if column == "advanced_parameters_used":
        if isinstance(value, str):
            value = value.strip().lower() in {"true", "1", "yes"}
        return yes_no(bool(value), lang)
    if column == "role":
        return translate_role(value, lang)
    if column == "preferred_language":
        return translate_language_name(normalize_language_code(value), lang)
    return value


def localize_dataframe(dataframe: pd.DataFrame, lang: str) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    localized = dataframe.copy()
    translatable_columns = {
        "gender",
        "bmi_category",
        "predicted_risk",
        "smoking_habit",
        "model_name",
        "advanced_parameters_used",
        "role",
        "preferred_language",
    }
    for column in translatable_columns.intersection(localized.columns):
        localized[column] = localized[column].apply(lambda value: translate_display_value(column, value, lang))

    localized.columns = [translate_column_name(str(column), lang) for column in localized.columns]
    return localized


def clear_prediction_cache() -> None:
    st.session_state["run_prediction"] = False
    st.session_state["prediction_request"] = None
    st.session_state["prediction_cache_key"] = None
    st.session_state["prediction_base_result"] = None


def render_auth_page(base_url: str, lang: str, message: str | None = None) -> None:
    st.markdown("---")
    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.2, 1])
    with auth_col2:
        st.subheader(t("auth_login_required", lang))
        st.markdown(t("auth_use_account", lang))
        if message:
            st.warning(message)

        login_tab, register_tab = st.tabs([t("login", lang), t("register", lang)])
        with login_tab:
            with st.form("main_api_login_form"):
                login_email = st.text_input(t("email", lang), key="main_login_email")
                login_password = st.text_input(t("password", lang), type="password", key="main_login_password")
                login_submit = st.form_submit_button(t("login", lang), use_container_width=True)
                if login_submit:
                    try:
                        token_data = login_user(base_url, login_email, login_password)
                        st.session_state["api_token"] = token_data["access_token"]
                        st.session_state["api_user"] = get_current_user(base_url, token_data["access_token"])
                        st.session_state["language_synced_user_id"] = None
                        sync_language_from_api_user()
                        st.success(t("login_success", lang))
                        st.rerun()
                    except Exception as exc:
                        st.error(t("login_failed", lang))
                        st.code(str(exc), language=None)

        with register_tab:
            with st.form("main_api_register_form"):
                reg_username = st.text_input(t("username", lang), key="main_reg_username")
                reg_email = st.text_input(t("register_email", lang), key="main_reg_email")
                reg_password = st.text_input(t("register_password", lang), type="password", key="main_reg_password")
                reg_submit = st.form_submit_button(t("register", lang), use_container_width=True)
                if reg_submit:
                    try:
                        register_user(base_url, reg_username, reg_email, reg_password, preferred_language=lang)
                        st.success(t("registration_success", lang))
                    except Exception as exc:
                        st.error(t("registration_failed", lang))
                        st.code(str(exc), language=None)


def render_admin_dashboard(base_url: str, token: str, current_user: Dict[str, Any], lang: str) -> None:
    st.subheader(t("admin_dashboard", lang))
    st.markdown(t("admin_monitor", lang))

    try:
        stats = get_admin_stats(base_url, token)
        users = get_admin_users(base_url, token)
        predictions = get_admin_predictions(base_url, token)
    except Exception as exc:
        st.error(t("admin_dashboard_failed", lang, error=exc))
        st.stop()

    metric_cols = st.columns(4)
    metric_cols[0].metric(t("total_users", lang), stats.get("total_users", 0))
    metric_cols[1].metric(t("total_admins", lang), stats.get("total_admins", 0))
    metric_cols[2].metric(t("total_predictions", lang), stats.get("total_predictions", 0))
    metric_cols[3].metric(t("logged_in_role", lang), translate_role(current_user.get("role", "admin"), lang))

    risk_distribution = stats.get("risk_distribution", {})
    risk_df = pd.DataFrame(
        {
            t("risk_category", lang): [translate_risk(item, lang) for item in risk_distribution.keys()],
            "Count": list(risk_distribution.values()),
        }
    )

    top_cols = st.columns([1, 1])
    with top_cols[0]:
        st.markdown(f"**{t('risk_distribution_across_predictions', lang)}**")
        if not risk_df.empty:
            st.bar_chart(risk_df.set_index(t("risk_category", lang)))
        else:
            st.info(t("no_prediction_data", lang))

    with top_cols[1]:
        st.markdown(f"**{t('admin_summary', lang)}**")
        st.info(t("admin_summary_text", lang, email=current_user.get("email")))

    admin_tab1, admin_tab2, admin_tab3 = st.tabs([t("recent_activity", lang), t("all_users", lang), t("all_predictions", lang)])

    with admin_tab1:
        st.markdown(f"**{t('recent_users', lang)}**")
        recent_users = pd.DataFrame(stats.get("recent_users", []))
        if not recent_users.empty:
            if "created_at" in recent_users.columns:
                recent_users["created_at"] = recent_users["created_at"].astype(str)
            st.dataframe(localize_dataframe(recent_users, lang), use_container_width=True)
        else:
            st.info(t("no_users_available", lang))

        st.markdown(f"**{t('recent_predictions', lang)}**")
        recent_predictions = pd.DataFrame(stats.get("recent_predictions", []))
        if not recent_predictions.empty:
            if "created_at" in recent_predictions.columns:
                recent_predictions["created_at"] = recent_predictions["created_at"].astype(str)
            trimmed_columns = [col for col in recent_predictions.columns if col not in {"probabilities", "recommendations", "alerts", "context_data"}]
            st.dataframe(localize_dataframe(recent_predictions[trimmed_columns], lang), use_container_width=True)
        else:
            st.info(t("no_predictions_available", lang))

    with admin_tab2:
        users_df = pd.DataFrame(users)
        if not users_df.empty:
            if "created_at" in users_df.columns:
                users_df["created_at"] = users_df["created_at"].astype(str)
            st.dataframe(localize_dataframe(users_df, lang), use_container_width=True)
        else:
            st.info(t("no_user_records", lang))

    with admin_tab3:
        predictions_df = pd.DataFrame(predictions)
        if not predictions_df.empty:
            if "created_at" in predictions_df.columns:
                predictions_df["created_at"] = predictions_df["created_at"].astype(str)
            trimmed_columns = [col for col in predictions_df.columns if col not in {"probabilities", "recommendations", "alerts", "context_data"}]
            st.dataframe(localize_dataframe(predictions_df[trimmed_columns], lang), use_container_width=True)
        else:
            st.info(t("no_prediction_records", lang))

    st.markdown("---")
    st.caption(t("admin_api_caption", lang))


def build_payload(model_name: str, values: Dict[str, float], context: Dict[str, Any], include_advanced: bool) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model_name": model_name,
        "diet_score": float(values["diet_score"]),
        "sleep_hours": float(values["sleep_hours"]),
        "activity_level": float(values["activity_level"]),
        "bmi": float(values["bmi"]),
        "age": context.get("age"),
        "gender": context.get("gender"),
        "height_cm": context.get("height_cm"),
        "weight_kg": context.get("weight_kg"),
        "calorie_activity": context.get("calorie_activity"),
    }
    if include_advanced:
        payload.update(
            {
                "blood_pressure_systolic": context.get("blood_pressure_systolic"),
                "blood_pressure_diastolic": context.get("blood_pressure_diastolic"),
                "blood_sugar": context.get("blood_sugar"),
                "smoking_habit": context.get("smoking_habit"),
                "screen_time_hours": context.get("screen_time_hours"),
                "stress_level": context.get("stress_level"),
            }
        )
    return payload


def local_prediction_base(bundle: Dict[str, Any], model_name: str, values: Dict[str, float]) -> Dict[str, Any]:
    user_data = build_user_feature_dict(**values)
    input_df = pd.DataFrame([{feature: user_data[feature] for feature in FEATURE_COLUMNS}])
    predicted_risk, probabilities = predict_single(bundle, input_df, model_name)
    return {
        "user_data": user_data,
        "predicted_risk": predicted_risk,
        "probabilities": {label: float(prob) for label, prob in zip(bundle["label_classes"], probabilities)},
        "advanced_parameters_used": False,
    }


def api_prediction_base(base_url: str, token: str, model_name: str, values: Dict[str, float], context: Dict[str, Any], include_advanced: bool) -> Dict[str, Any]:
    payload = build_payload(model_name, values, context, include_advanced)
    response = api_predict(base_url, token, payload)
    user_data = build_user_feature_dict(**values)
    return {
        "user_data": user_data,
        "predicted_risk": response["predicted_risk"],
        "probabilities": {label: float(prob) for label, prob in response["probabilities"].items()},
        "advanced_parameters_used": response.get("advanced_parameters_used", include_advanced),
    }


def build_prediction_display(base_result: Dict[str, Any], values: Dict[str, float], context: Dict[str, Any], include_advanced: bool, calorie_profile: Dict[str, Any] | None, lang: str) -> Dict[str, Any]:
    predicted_risk = str(base_result["predicted_risk"])
    explanation = generate_explainability_text(**values, lang=lang)
    recommendations = generate_recommendations(
        predicted_risk=predicted_risk,
        blood_pressure_systolic=context.get("blood_pressure_systolic") if include_advanced else None,
        blood_pressure_diastolic=context.get("blood_pressure_diastolic") if include_advanced else None,
        blood_sugar=context.get("blood_sugar") if include_advanced else None,
        smoking_habit=context.get("smoking_habit") if include_advanced else None,
        screen_time_hours=context.get("screen_time_hours") if include_advanced else None,
        stress_level=context.get("stress_level") if include_advanced else None,
        lang=lang,
        **values,
    )
    alert_items = generate_health_alerts(
        sleep_hours=values["sleep_hours"],
        bmi=values["bmi"],
        predicted_risk=predicted_risk,
        blood_pressure_systolic=context.get("blood_pressure_systolic") if include_advanced else None,
        blood_pressure_diastolic=context.get("blood_pressure_diastolic") if include_advanced else None,
        blood_sugar=context.get("blood_sugar") if include_advanced else None,
        smoking_habit=context.get("smoking_habit") if include_advanced else None,
        screen_time_hours=context.get("screen_time_hours") if include_advanced else None,
        stress_level=context.get("stress_level") if include_advanced else None,
        lang=lang,
    )
    calorie_summary = calorie_guidance_text(calorie_profile, lang=lang) if calorie_profile else None
    return {
        **base_result,
        "explanation": explanation,
        "recommendations": recommendations,
        "alerts": [message for _, message in alert_items],
        "alert_items": alert_items,
        "calorie_summary": calorie_summary,
    }


def get_history_dataframe(use_api: bool, base_url: str, token: str | None) -> pd.DataFrame:
    if use_api and token:
        history_items = get_history(base_url, token)
        if not history_items:
            return pd.DataFrame()
        history_df = pd.DataFrame(history_items)
        if "created_at" in history_df.columns:
            history_df["timestamp"] = pd.to_datetime(history_df["created_at"], errors="coerce")
        return history_df
    return load_prediction_history()


def build_additional_sections(
    context: Dict[str, Any],
    include_advanced: bool,
    diet_result: Dict[str, Any] | None,
    contribution_df: pd.DataFrame,
    calorie_summary: str | None,
    alerts: List[str],
    lang: str,
) -> List[tuple[str, str]]:
    blood_pressure_label = "Blood Pressure" if lang == "en" else "रक्तचाप"
    screen_time_label = "Screen Time" if lang == "en" else "स्क्रीन टाइम"

    additional_context_lines = [
        f"- {t('age', lang)}: {context.get('age')}",
        f"- {t('gender', lang)}: {translate_gender(context.get('gender'), lang)}",
        f"- {t('height_cm', lang)}: {context.get('height_cm')}",
        f"- {t('weight_kg', lang)}: {context.get('weight_kg')}",
        f"- {translate_column_name('advanced_parameters_used', lang)}: {yes_no(include_advanced, lang)}",
    ]
    if include_advanced:
        additional_context_lines.extend(
            [
                f"- {blood_pressure_label}: {format_optional(context.get('blood_pressure_systolic'), lang=lang)}/{format_optional(context.get('blood_pressure_diastolic'), lang=lang)} mmHg",
                f"- {t('blood_sugar', lang)}: {format_optional(context.get('blood_sugar'), ' mg/dL', lang)}",
                f"- {t('smoking_habit', lang)}: {format_optional(translate_smoking_habit(context.get('smoking_habit'), lang), lang=lang)}",
                f"- {screen_time_label}: {format_optional(context.get('screen_time_hours'), ' hours/day', lang)}",
                f"- {t('stress_level', lang)}: {format_optional(context.get('stress_level'), ' / 10', lang)}",
            ]
        )

    sections = [
        (t("additional_health_context", lang), "\n".join(additional_context_lines)),
        (t("health_alerts", lang), "\n".join(f"- {item}" for item in alerts)),
        (t("calorie_guidance", lang), calorie_summary or t("not_available", lang)),
        (
            t("hrs_breakdown", lang),
            "\n".join(
                [
                    f"- {t('diet_risk_contribution', lang)}: {contribution_df.iloc[0]['Contribution']}",
                    f"- {t('sleep_risk_contribution', lang)}: {contribution_df.iloc[1]['Contribution']}",
                    f"- {t('activity_risk_contribution', lang)}: {contribution_df.iloc[2]['Contribution']}",
                    f"- {t('bmi_risk_contribution', lang)}: {contribution_df.iloc[3]['Contribution']}",
                ]
            ),
        ),
    ]
    if diet_result:
        sections.append(
            (
                t("diet_score_breakdown_section", lang),
                "\n".join(
                    [
                        f"- {t('diet_score', lang)}: {diet_result['diet_score']}",
                        f"- {t('fruits_veg_score', lang)}: {diet_result['fruits_veg_score']}",
                        f"- {t('water_score', lang)}: {diet_result['water_score']}",
                        f"- {t('breakfast_score', lang)}: {diet_result['breakfast_score']}",
                        f"- {t('protein_score', lang)}: {diet_result['protein_score']}",
                        f"- {t('junk_food_penalty', lang)}: {diet_result['junk_food_penalty']}",
                        f"- {t('sugary_drinks_penalty', lang)}: {diet_result['sugary_drinks_penalty']}",
                    ]
                ),
            )
        )
    return sections


def render_food_checker_section(current_values: Dict[str, float], current_context: Dict[str, Any], predicted_risk: str | None, lang: str) -> None:
    st.markdown("---")
    st.subheader(f"🍽️ {t('food_checker_title', lang)}")
    st.markdown(t("food_checker_intro", lang))
    st.caption(t("food_lightweight_note", lang))
    st.caption(t("food_profile_context", lang))

    food_control_cols = st.columns(2)
    with food_control_cols[0]:
        cuisine_hint = st.selectbox(
            t("food_cuisine_hint", lang),
            list_cuisine_hints(),
            index=0,
            format_func=lambda value: translate_cuisine_hint(value, lang),
            key="food_checker_cuisine_hint",
        )
    with food_control_cols[1]:
        st.caption(t("food_cuisine_hint_note", lang))

    uploaded_file = st.file_uploader(
        t("food_upload_label", lang),
        type=["jpg", "jpeg", "png", "webp"],
        key="food_checker_upload",
    )
    if not uploaded_file:
        return

    analysis = analyze_food_image(uploaded_file, cuisine_hint=cuisine_hint)
    food_image = analysis["image"]
    supported_foods = get_ordered_food_options(cuisine_hint)
    auto_detected_food = analysis.get("auto_detected_food")
    auto_confidence = int(round(float(analysis.get("auto_confidence", 0.0)) * 100))

    st.image(food_image, caption=getattr(uploaded_file, "name", "food image"), use_container_width=True)

    if auto_detected_food:
        st.info(t("food_auto_guess", lang, food=translate_food_name(str(auto_detected_food), lang), confidence=auto_confidence))

    candidate_text = ", ".join(
        f"{translate_food_name(str(item['food_name']), lang)} ({int(round(float(item['confidence']) * 100))}%)"
        for item in analysis.get("candidates", [])
    )
    if candidate_text:
        st.caption(f"{t('food_candidates', lang)}: {candidate_text}")

    if cuisine_hint == "South Indian":
        st.success(t("food_south_indian_hint_active", lang))

    food_default_index = supported_foods.index(auto_detected_food) if auto_detected_food in supported_foods else 0
    selection_cols = st.columns(2)
    with selection_cols[0]:
        selected_food = st.selectbox(
            t("food_manual_confirm", lang),
            supported_foods,
            index=food_default_index,
            format_func=lambda value: translate_food_name(value, lang),
            key="food_checker_selected_food",
        )
    with selection_cols[1]:
        portion_size = st.selectbox(
            t("food_portion_size", lang),
            ["Small", "Standard", "Large"],
            index=1,
            format_func=lambda value: translate_portion_size(value, lang),
            key="food_checker_portion_size",
        )

    food_result = build_food_recommendation(
        selected_food,
        portion_size,
        predicted_risk=predicted_risk,
        bmi=current_values.get("bmi"),
        blood_sugar=current_context.get("blood_sugar"),
        diet_score=current_values.get("diet_score"),
        lang=lang,
    )

    metric_cols = st.columns(3)
    metric_cols[0].metric(t("food_manual_confirm", lang), food_result["food_name_display"])
    metric_cols[1].metric(t("food_estimated_calories", lang), f"{food_result['estimated_calories']} kcal")
    metric_cols[2].metric(t("food_decision", lang), food_result["decision_label_display"])

    if food_result["decision_label"] == "Recommended":
        st.success(food_result["decision_label_display"])
    elif food_result["decision_label"] == "Consume in moderation":
        st.warning(food_result["decision_label_display"])
    else:
        st.error(food_result["decision_label_display"])

    detail_cols = st.columns(2)
    with detail_cols[0]:
        st.markdown(f"**{t('food_serving_size', lang)}**")
        st.write(food_result["serving_size"])
        st.markdown(f"**{t('food_primary_reason', lang)}**")
        st.write(food_result["primary_reason"])
    with detail_cols[1]:
        st.markdown(f"**{t('food_portion_size', lang)}**")
        st.write(food_result["portion_size_display"])
        st.markdown(f"**{t('food_positive_note', lang)}**")
        st.write(food_result["positive_reason"])

    alternative = str(food_result.get("healthier_alternative_display") or "").strip()
    if alternative:
        st.markdown(f"**{t('food_better_alternative', lang)}**")
        st.write(alternative)

    context_parts = [
        f"BMI: {current_values.get('bmi')}",
        f"{t('diet_score', lang)}: {current_values.get('diet_score')}",
    ]
    if predicted_risk:
        context_parts.append(f"{t('predicted_risk', lang)}: {translate_risk(predicted_risk, lang)}")
    if not is_missing(current_context.get("blood_sugar")):
        context_parts.append(f"{t('blood_sugar', lang)}: {current_context.get('blood_sugar')} mg/dL")
    st.caption(" | ".join(context_parts))

    st.markdown(f"**{t('food_disclaimer_label', lang)}**")
    st.caption(food_result["disclaimer"])


inject_custom_css()
init_session_state()
bundle = get_model_bundle()

initial_backend_url = st.session_state.get("backend_url", "http://127.0.0.1:8000")
if st.session_state.get("api_mode") and st.session_state.get("api_token") and not st.session_state.get("api_user"):
    try:
        st.session_state["api_user"] = get_current_user(initial_backend_url, st.session_state["api_token"])
    except Exception:
        st.session_state["api_token"] = None
        st.session_state["api_user"] = None
        st.session_state["language_synced_user_id"] = None

sync_language_from_api_user()
language_index = LANGUAGE_OPTIONS.index(st.session_state.get("language", "en")) if st.session_state.get("language", "en") in LANGUAGE_OPTIONS else 0
lang = st.sidebar.selectbox(
    "Language / भाषा",
    LANGUAGE_OPTIONS,
    index=language_index,
    format_func=lambda code: translate_language_name(code, code),
)
st.session_state["language"] = lang

st.title(t("app_title", lang))
st.markdown(t("app_intro", lang))

st.sidebar.header(t("sidebar_header", lang))
st.sidebar.info(t("sidebar_info", lang))
model_name = st.sidebar.selectbox(t("prediction_model", lang), MODEL_OPTIONS, index=0, format_func=lambda value: translate_model_name(value, lang))
diet_input_mode = st.sidebar.radio(t("diet_input_mode", lang), DIET_INPUT_OPTIONS, index=0, format_func=lambda value: translate_diet_input_mode(value, lang))
bmi_input_mode = st.sidebar.radio(t("bmi_input_mode", lang), BMI_INPUT_OPTIONS, index=0, format_func=lambda value: translate_bmi_input_mode(value, lang))
include_advanced = st.sidebar.checkbox(t("include_advanced", lang), value=False)
use_api_mode = st.sidebar.checkbox(t("use_fastapi_backend", lang), value=st.session_state.get("api_mode", False))
backend_url = st.sidebar.text_input(t("backend_url", lang), value=st.session_state.get("backend_url", "http://127.0.0.1:8000"))
st.session_state["backend_url"] = backend_url
st.session_state["api_mode"] = use_api_mode

if st.sidebar.button(t("check_backend_status", lang)):
    try:
        health_check(backend_url)
        st.sidebar.success(t("backend_reachable", lang))
    except Exception as exc:
        st.sidebar.error(t("backend_check_failed", lang, error=exc))

with st.sidebar.expander(t("api_authentication", lang), expanded=use_api_mode):
    if use_api_mode:
        if st.session_state.get("api_user"):
            st.caption(t("logged_in_as", lang, email=st.session_state['api_user'].get('email')))
            st.caption(t("role_caption", lang, role=translate_role(st.session_state['api_user'].get('role', 'user'), lang)))
            if st.button(t("logout", lang), key="logout_api"):
                st.session_state["api_token"] = None
                st.session_state["api_user"] = None
                st.session_state["language_synced_user_id"] = None
                clear_prediction_cache()
                st.rerun()
        else:
            st.caption(t("login_or_register_caption", lang))
    else:
        st.caption(t("enable_api_mode_caption", lang))

if use_api_mode and st.session_state.get("api_token") and not st.session_state.get("api_user"):
    try:
        st.session_state["api_user"] = get_current_user(backend_url, st.session_state["api_token"])
        sync_language_from_api_user()
    except Exception:
        st.session_state["api_token"] = None
        st.session_state["api_user"] = None
        st.session_state["language_synced_user_id"] = None

if use_api_mode and not st.session_state.get("api_token"):
    render_auth_page(backend_url, lang)
    st.stop()

if use_api_mode and not st.session_state.get("api_user"):
    render_auth_page(backend_url, lang, message=t("session_invalid_message", lang))
    st.stop()

if use_api_mode and st.session_state.get("api_user") and st.session_state.get("api_token"):
    stored_language = normalize_language_code((st.session_state.get("api_user") or {}).get("preferred_language", "en"))
    if lang != stored_language:
        try:
            updated_user = update_language_preference(backend_url, st.session_state["api_token"], lang)
            st.session_state["api_user"] = updated_user
            st.session_state["language_synced_user_id"] = updated_user.get("id")
            st.sidebar.caption(t("language_preference_saved", lang, language=translate_language_name(lang, lang)))
        except Exception as exc:
            st.sidebar.warning(t("language_preference_save_failed", lang, error=exc))

current_user_role = (st.session_state.get("api_user", {}) or {}).get("role", "user") if use_api_mode else "user"
admin_view_mode = "User Dashboard"
if use_api_mode and current_user_role == "admin":
    admin_view_mode = st.sidebar.radio(t("admin_view", lang), ADMIN_VIEW_OPTIONS, index=0, format_func=lambda value: translate_admin_view_mode(value, lang))
    if admin_view_mode == "Admin Dashboard":
        render_admin_dashboard(backend_url, st.session_state["api_token"], st.session_state["api_user"], lang)
        st.stop()

summary_cols = st.columns(3)
summary_cols[0].info(t("core_prediction_inputs", lang))
summary_cols[1].info(t("optional_advanced_inputs", lang))
summary_cols[2].info(t("smart_outputs", lang))

st.info(t("practical_design", lang))

left_col, right_col = st.columns([1.45, 1])

with left_col:
    st.subheader(t("user_input_section", lang))
    basic_col1, basic_col2 = st.columns(2)
    with basic_col1:
        age = st.number_input(t("age", lang), min_value=15, max_value=90, value=21)
        gender = st.selectbox(t("gender", lang), GENDER_OPTIONS, format_func=lambda value: translate_gender(value, lang))
        height_cm = st.number_input(t("height_cm", lang), min_value=120.0, max_value=220.0, value=160.0, step=0.5)
    with basic_col2:
        weight_kg = st.number_input(t("weight_kg", lang), min_value=30.0, max_value=180.0, value=60.0, step=0.5)
        calorie_activity = st.selectbox(
            t("calorie_activity", lang),
            CALORIE_ACTIVITY_OPTIONS,
            index=2,
            format_func=lambda value: translate_activity_type(value, lang),
        )

    st.markdown(f"### {t('diet_assessment', lang)}")
    if diet_input_mode == "Calculate Diet Score":
        diet_col1, diet_col2 = st.columns(2)
        with diet_col1:
            fruits_veg_servings = st.slider(t("fruits_veg_servings", lang), 0, 8, 3)
            water_liters_per_day = st.slider(t("water_intake", lang), 0.0, 5.0, 2.0, 0.1)
            breakfast_days_per_week = st.slider(t("breakfast_days", lang), 0, 7, 5)
        with diet_col2:
            protein_days_per_week = st.slider(t("protein_days", lang), 0, 7, 4)
            junk_food_meals_per_week = st.slider(t("junk_food_meals", lang), 0, 14, 3)
            sugary_drinks_per_week = st.slider(t("sugary_drinks", lang), 0, 14, 3)
        diet_result = calculate_diet_score(
            fruits_veg_servings=fruits_veg_servings,
            junk_food_meals_per_week=junk_food_meals_per_week,
            sugary_drinks_per_week=sugary_drinks_per_week,
            water_liters_per_day=water_liters_per_day,
            breakfast_days_per_week=breakfast_days_per_week,
            protein_days_per_week=protein_days_per_week,
        )
        diet_score = float(diet_result["diet_score"])
        st.success(t("calculated_diet_score", lang, score=diet_score))
    else:
        diet_score = float(st.slider(t("diet_score", lang), 0, 100, 60))
        diet_result = None

    st.markdown(f"### {t('core_lifestyle_inputs', lang)}")
    lifestyle_col1, lifestyle_col2 = st.columns(2)
    with lifestyle_col1:
        sleep_hours = st.slider(t("sleep_hours", lang), 3.0, 10.0, 7.0, 0.1)
    with lifestyle_col2:
        activity_level = st.slider(t("activity_level", lang), 0.0, 10.0, 5.0, 0.1)

    st.markdown(f"### {t('bmi_calorie_section', lang)}")
    calculated_bmi = calculate_bmi(weight_kg=weight_kg, height_cm=height_cm)
    if bmi_input_mode == "Calculate BMI from Height & Weight":
        bmi = float(calculated_bmi)
        st.success(t("calculated_bmi", lang, bmi=bmi))
    else:
        bmi = float(st.slider(t("manual_bmi", lang), 15.0, 40.0, float(calculated_bmi), 0.1))
        st.caption(t("reference_bmi", lang, bmi=calculated_bmi))

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
        st.markdown(f"### {t('advanced_optional_inputs', lang)}")
        adv_col1, adv_col2 = st.columns(2)
        with adv_col1:
            advanced_values["screen_time_hours"] = float(st.slider(t("screen_time_per_day", lang), 0.0, 16.0, 6.0, 0.5))
            advanced_values["stress_level"] = int(st.slider(t("stress_level", lang), 0, 10, 5))
            advanced_values["smoking_habit"] = st.selectbox(t("smoking_habit", lang), SMOKING_OPTIONS, format_func=lambda value: translate_smoking_habit(value, lang))
        with adv_col2:
            advanced_values["blood_pressure_systolic"] = int(st.number_input(t("blood_pressure_systolic", lang), min_value=80, max_value=220, value=120))
            advanced_values["blood_pressure_diastolic"] = int(st.number_input(t("blood_pressure_diastolic", lang), min_value=50, max_value=140, value=80))
            advanced_values["blood_sugar"] = float(st.number_input(t("blood_sugar", lang), min_value=60.0, max_value=350.0, value=100.0, step=1.0))
    else:
        st.info(t("advanced_optional_info", lang))

    if st.button(t("predict_button", lang), type="primary", use_container_width=True):
        if use_api_mode and not st.session_state.get("api_token"):
            st.error(t("api_login_required_before_predict", lang))
        else:
            st.session_state["run_prediction"] = True
            st.session_state["prediction_request"] = {
                "model_name": model_name,
                "prediction_source": "api" if use_api_mode else "local",
                "backend_url": backend_url,
                "input_values": {
                    "diet_score": float(diet_score),
                    "sleep_hours": float(sleep_hours),
                    "activity_level": float(activity_level),
                    "bmi": float(bmi),
                },
                "context_values": {
                    "age": int(age),
                    "gender": gender,
                    "height_cm": float(height_cm),
                    "weight_kg": float(weight_kg),
                    "calorie_activity": calorie_activity,
                    "include_advanced": include_advanced,
                    **advanced_values,
                },
                "diet_result": diet_result,
                "calorie_profile": calorie_profile,
            }
            st.session_state["prediction_source"] = "api" if use_api_mode else "local"
            st.session_state["prediction_cache_key"] = None
            st.session_state["prediction_base_result"] = None

with right_col:
    st.subheader(t("system_overview", lang))
    st.markdown(t("system_overview_bullets", lang))
    st.info(t("core_ml_info", lang))
    st.success(
        t(
            "current_input_mode",
            lang,
            diet_mode=translate_diet_input_mode(diet_input_mode, lang),
            bmi_mode=translate_bmi_input_mode(bmi_input_mode, lang),
            advanced=t("enabled", lang) if include_advanced else t("disabled", lang),
            execution=t("backend_fastapi_mode", lang) if use_api_mode else t("backend_local_mode", lang),
        )
    )

latest_predicted_risk: str | None = None
prediction_request = st.session_state.get("prediction_request")
if st.session_state.get("run_prediction") and prediction_request:
    selected_model_name = str(prediction_request["model_name"])
    values = dict(prediction_request["input_values"])
    context = dict(prediction_request.get("context_values", {}))
    include_advanced = bool(context.get("include_advanced", False))
    calorie_profile = prediction_request.get("calorie_profile")
    diet_result = prediction_request.get("diet_result")

    cache_key = json.dumps(
        {
            "prediction_source": prediction_request.get("prediction_source"),
            "backend_url": prediction_request.get("backend_url"),
            "model_name": selected_model_name,
            "values": values,
            "context": context,
        },
        sort_keys=True,
        default=str,
    )

    try:
        if st.session_state.get("prediction_cache_key") != cache_key or st.session_state.get("prediction_base_result") is None:
            if prediction_request.get("prediction_source") == "api":
                base_result = api_prediction_base(
                    prediction_request.get("backend_url", backend_url),
                    st.session_state["api_token"],
                    selected_model_name,
                    values,
                    context,
                    include_advanced,
                )
            else:
                base_result = local_prediction_base(bundle, selected_model_name, values)
                base_result["advanced_parameters_used"] = include_advanced
                append_prediction_history(
                    {
                        "model_name": selected_model_name,
                        "age": context.get("age"),
                        "gender": context.get("gender"),
                        "diet_score": round(base_result["user_data"]["diet_score"], 2),
                        "sleep_hours": round(base_result["user_data"]["sleep_hours"], 2),
                        "activity_level": round(base_result["user_data"]["activity_level"], 2),
                        "bmi": round(base_result["user_data"]["bmi"], 2),
                        "bmi_category": base_result["user_data"]["bmi_category"],
                        "hrs_score": round(base_result["user_data"]["hrs_score"], 2),
                        "predicted_risk": base_result["predicted_risk"],
                        "advanced_parameters_used": include_advanced,
                        "blood_pressure_systolic": context.get("blood_pressure_systolic") if include_advanced else None,
                        "blood_pressure_diastolic": context.get("blood_pressure_diastolic") if include_advanced else None,
                        "blood_sugar": context.get("blood_sugar") if include_advanced else None,
                        "smoking_habit": context.get("smoking_habit") if include_advanced else None,
                        "screen_time_hours": context.get("screen_time_hours") if include_advanced else None,
                        "stress_level": context.get("stress_level") if include_advanced else None,
                    }
                )

            st.session_state["prediction_cache_key"] = cache_key
            st.session_state["prediction_base_result"] = base_result
        else:
            base_result = st.session_state["prediction_base_result"]
    except (ApiClientError, Exception) as exc:
        st.error(t("prediction_failed", lang, error=exc))
        st.stop()

    result = build_prediction_display(base_result, values, context, include_advanced, calorie_profile, lang)

    user_data = result["user_data"]
    predicted_risk = result["predicted_risk"]
    latest_predicted_risk = predicted_risk
    explanation = result["explanation"]
    recommendations = result["recommendations"]
    alerts = result["alerts"]
    alert_items = result["alert_items"]
    probability_map = result["probabilities"]
    calorie_summary = result["calorie_summary"]

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
    display_contribution_df = contribution_df.copy()
    display_contribution_df["Risk Component"] = display_contribution_df["Risk Component"].apply(lambda value: translate_risk_component(value, lang))

    additional_sections = build_additional_sections(context, include_advanced, diet_result, contribution_df, calorie_summary, alerts, lang)
    report_text = build_text_report(
        diet_score=user_data["diet_score"],
        sleep_hours=user_data["sleep_hours"],
        activity_level=user_data["activity_level"],
        bmi=user_data["bmi"],
        bmi_category=user_data["bmi_category"],
        hrs_score=user_data["hrs_score"],
        predicted_risk=predicted_risk,
        model_name=selected_model_name,
        explainability_text=explanation,
        recommendations=recommendations,
        additional_sections=additional_sections,
        lang=lang,
    )

    blood_pressure_label = "Blood Pressure" if lang == "en" else "रक्तचाप"
    screen_time_label = "Screen Time" if lang == "en" else "स्क्रीन टाइम"
    hours_per_day_suffix = " hours/day" if lang == "en" else " घंटे/दिन"

    pdf_input_rows = [
        (t("age", lang), str(context.get("age"))),
        (t("gender", lang), translate_gender(context.get("gender"), lang)),
        (t("height_cm", lang), str(context.get("height_cm"))),
        (t("weight_kg", lang), str(context.get("weight_kg"))),
        (t("diet_score", lang), f"{user_data['diet_score']:.2f}"),
        (t("sleep_hours", lang), f"{user_data['sleep_hours']:.2f}"),
        (t("activity_level", lang), f"{user_data['activity_level']:.2f}"),
        ("BMI", f"{user_data['bmi']:.2f}"),
        (t("bmi_category", lang), translate_bmi_category(user_data["bmi_category"], lang)),
        (translate_column_name("advanced_parameters_used", lang), yes_no(include_advanced, lang)),
        (blood_pressure_label, f"{format_optional(context.get('blood_pressure_systolic'), lang=lang)}/{format_optional(context.get('blood_pressure_diastolic'), lang=lang)} mmHg" if include_advanced else t("not_provided", lang)),
        (t("blood_sugar", lang), format_optional(context.get("blood_sugar"), " mg/dL", lang) if include_advanced else t("not_provided", lang)),
        (t("smoking_habit", lang), translate_smoking_habit(context.get("smoking_habit"), lang) if include_advanced and not is_missing(context.get("smoking_habit")) else t("not_provided", lang)),
        (screen_time_label, format_optional(context.get("screen_time_hours"), hours_per_day_suffix, lang) if include_advanced else t("not_provided", lang)),
        (t("stress_level", lang), format_optional(context.get("stress_level"), " / 10", lang) if include_advanced else t("not_provided", lang)),
    ]
    pdf_output_rows = [
        (t("hrs_score", lang), f"{user_data['hrs_score']:.2f}"),
        (t("predicted_risk", lang), translate_risk(predicted_risk, lang)),
        (t("selected_model", lang), translate_model_name(selected_model_name, lang)),
        (t("tab_explanation", lang), explanation),
        (t("calorie_guidance", lang), calorie_summary or t("not_available", lang)),
    ]
    pdf_bytes = build_pdf_report_bytes(
        input_rows=pdf_input_rows,
        output_rows=pdf_output_rows,
        recommendations=recommendations,
        alerts=alerts,
        additional_sections=additional_sections,
        language=lang,
    )

    try:
        history_df = get_history_dataframe(prediction_request.get("prediction_source") == "api", prediction_request.get("backend_url", backend_url), st.session_state.get("api_token"))
    except Exception as exc:
        history_df = pd.DataFrame()
        st.warning(t("history_load_failed", lang, error=exc))

    st.markdown("---")
    st.subheader(t("prediction_result", lang))
    metric_cols = st.columns(4)
    metric_cols[0].metric(t("hrs_score", lang), f"{user_data['hrs_score']:.2f}")
    metric_cols[1].metric(t("predicted_risk", lang), translate_risk(predicted_risk, lang))
    metric_cols[2].metric(t("bmi_category", lang), translate_bmi_category(user_data["bmi_category"], lang))
    metric_cols[3].metric(t("selected_model", lang), translate_model_name(selected_model_name, lang))

    st.markdown(
        f"<div style='padding:14px;border-radius:14px;background-color:{risk_color(predicted_risk)};color:white;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,0.10);'>{t('predicted_health_risk_category', lang, risk=translate_risk(predicted_risk, lang))}</div>",
        unsafe_allow_html=True,
    )

    prob_df = pd.DataFrame({t("risk_category", lang): [translate_risk(key, lang) for key in probability_map.keys()], t("probability", lang): list(probability_map.values())})
    st.bar_chart(prob_df.set_index(t("risk_category", lang)))

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            t("tab_explanation", lang),
            t("tab_recommendations", lang),
            t("tab_diet_calories", lang),
            t("tab_alerts_history", lang),
            t("tab_simulation", lang),
            t("tab_model_evaluation", lang),
            t("tab_download_reports", lang),
        ]
    )

    with tab1:
        st.write(explanation)
        st.caption(t("xai_summary_caption", lang))
        st.markdown(f"**{t('hrs_breakdown', lang)}**")
        st.bar_chart(display_contribution_df.set_index("Risk Component"))

    with tab2:
        for item in recommendations:
            st.write(f"- {item}")

    with tab3:
        if diet_result:
            st.markdown(f"**{t('diet_score_breakdown', lang)}**")
            st.write(
                {
                    t("diet_score", lang): diet_result["diet_score"],
                    t("fruits_veg_score", lang): diet_result["fruits_veg_score"],
                    t("water_score", lang): diet_result["water_score"],
                    t("breakfast_score", lang): diet_result["breakfast_score"],
                    t("protein_score", lang): diet_result["protein_score"],
                    t("junk_food_penalty", lang): diet_result["junk_food_penalty"],
                    t("sugary_drinks_penalty", lang): diet_result["sugary_drinks_penalty"],
                }
            )
        else:
            st.info(t("diet_score_entered_manually", lang))
        cal_cols = st.columns(3)
        cal_cols[0].metric(t("bmr", lang), f"{calorie_profile['bmr']} kcal/day")
        cal_cols[1].metric(t("maintenance_calories", lang), f"{calorie_profile['maintenance_calories']} kcal/day")
        cal_cols[2].metric(t("weight_loss_target", lang), f"{calorie_profile['weight_loss_target']} kcal/day")
        st.write(calorie_summary or t("not_available", lang))

    with tab4:
        st.markdown(f"**{t('health_alerts', lang)}**")
        for severity, message in alert_items:
            if severity == "error":
                st.error(message)
            elif severity == "warning":
                st.warning(message)
            elif severity == "success":
                st.success(message)
            else:
                st.info(message)

        st.markdown(f"**{t('user_prediction_history', lang)}**")
        if history_df.empty:
            st.info(t("no_saved_history", lang))
        else:
            history_display = history_df.copy()
            if "timestamp" in history_display.columns:
                history_display["timestamp"] = history_display["timestamp"].astype(str)
            if "created_at" in history_display.columns:
                history_display["created_at"] = history_display["created_at"].astype(str)
            st.dataframe(localize_dataframe(history_display.tail(10), lang), use_container_width=True)

            trend_df = history_df.dropna(subset=["timestamp"]).copy() if "timestamp" in history_df.columns else pd.DataFrame()
            if not trend_df.empty:
                trend_df = trend_df.set_index("timestamp")
                st.markdown(f"**{t('hrs_trend_over_time', lang)}**")
                st.line_chart(trend_df[["hrs_score"]])
                st.markdown(f"**{t('bmi_trend_over_time', lang)}**")
                st.line_chart(trend_df[["bmi"]])

            if "predicted_risk" in history_df.columns:
                risk_count_df = history_df["predicted_risk"].value_counts().rename_axis(t("risk_category", lang)).reset_index(name="Count")
                risk_count_df[t("risk_category", lang)] = risk_count_df[t("risk_category", lang)].apply(lambda value: translate_risk(value, lang))
                st.markdown(f"**{t('saved_risk_distribution', lang)}**")
                st.bar_chart(risk_count_df.set_index(t("risk_category", lang)))

    with tab5:
        st.markdown(f"**{t('try_improved_scenario', lang)}**")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            sim_diet = st.slider(t("scenario_diet_score", lang), 0, 100, int(round(values["diet_score"])), key="sim_diet")
            sim_sleep = st.slider(t("scenario_sleep_hours", lang), 3.0, 10.0, float(values["sleep_hours"]), 0.1, key="sim_sleep")
        with sim_col2:
            sim_activity = st.slider(t("scenario_activity_level", lang), 0.0, 10.0, float(values["activity_level"]), 0.1, key="sim_activity")
            sim_bmi = st.slider(t("scenario_bmi", lang), 15.0, 40.0, float(values["bmi"]), 0.1, key="sim_bmi")
        scenario_values = {"diet_score": float(sim_diet), "sleep_hours": float(sim_sleep), "activity_level": float(sim_activity), "bmi": float(sim_bmi)}
        scenario_user_data = build_user_feature_dict(**scenario_values)
        scenario_df = pd.DataFrame([{feature: scenario_user_data[feature] for feature in FEATURE_COLUMNS}])
        scenario_risk, scenario_probabilities = predict_single(bundle, scenario_df, selected_model_name)
        compare_cols = st.columns(2)
        with compare_cols[0]:
            st.markdown(f"**{t('current_prediction', lang)}**")
            st.write(
                {
                    t("hrs_score", lang): user_data["hrs_score"],
                    t("predicted_risk", lang): translate_risk(predicted_risk, lang),
                    t("bmi_category", lang): translate_bmi_category(user_data["bmi_category"], lang),
                }
            )
        with compare_cols[1]:
            st.markdown(f"**{t('scenario_prediction', lang)}**")
            st.write(
                {
                    t("hrs_score", lang): scenario_user_data["hrs_score"],
                    t("predicted_risk", lang): translate_risk(scenario_risk, lang),
                    t("bmi_category", lang): translate_bmi_category(scenario_user_data["bmi_category"], lang),
                }
            )
        hrs_delta = round(scenario_user_data["hrs_score"] - user_data["hrs_score"], 2)
        if hrs_delta < 0:
            st.success(t("scenario_improved", lang, points=abs(hrs_delta)))
        elif hrs_delta > 0:
            st.warning(t("scenario_increased", lang, points=hrs_delta))
        else:
            st.info(t("scenario_unchanged", lang))
        scenario_probability_label = "Scenario Probability" if lang == "en" else "परिदृश्य प्रायिकता"
        scenario_prob_df = pd.DataFrame({t("risk_category", lang): [translate_risk(item, lang) for item in bundle["label_classes"]], scenario_probability_label: scenario_probabilities})
        st.bar_chart(scenario_prob_df.set_index(t("risk_category", lang)))

    with tab6:
        st.pyplot(build_model_comparison_figure(bundle["metrics"]))
        eval_cols = st.columns(2)
        metric_heading_suffix = "Metrics" if lang == "en" else "मेट्रिक्स"
        for idx, eval_model_name in enumerate(["Logistic Regression", "Random Forest"]):
            with eval_cols[idx]:
                st.markdown(f"**{translate_model_name(eval_model_name, lang)} {metric_heading_suffix}**")
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
                        [translate_risk(item, lang) for item in bundle["label_classes"]],
                        f"{translate_model_name(eval_model_name, lang)} Confusion Matrix",
                    )
                )
        st.pyplot(build_feature_importance_figure(bundle["feature_importances"]))
        st.caption(
            "Feature names remain in English to match the trained model columns."
            if lang == "en"
            else "फ़ीचर नाम प्रशिक्षित मॉडल कॉलम से मेल खाने के लिए अंग्रेज़ी में रखे गए हैं।"
        )

    with tab7:
        st.download_button(t("download_pdf_report", lang), data=pdf_bytes, file_name="health_risk_report.pdf", mime="application/pdf", use_container_width=True)
        st.download_button(t("download_text_report", lang), data=report_text, file_name="health_risk_report.txt", mime="text/plain", use_container_width=True)
        st.text_area(t("text_report_preview", lang), report_text, height=360)
else:
    st.info(t("enter_values_info", lang))

if st.session_state.get("run_prediction") and prediction_request:
    current_food_values = {
        key: float(value)
        for key, value in dict(prediction_request.get("input_values", {})).items()
        if key in {"diet_score", "sleep_hours", "activity_level", "bmi"}
    }
    prediction_context_values = dict(prediction_request.get("context_values", {}))
    current_food_context = {
        "blood_sugar": prediction_context_values.get("blood_sugar") if prediction_context_values.get("include_advanced") else None,
    }
else:
    current_food_values = {
        "diet_score": float(diet_score),
        "sleep_hours": float(sleep_hours),
        "activity_level": float(activity_level),
        "bmi": float(bmi),
    }
    current_food_context = {
        "blood_sugar": advanced_values.get("blood_sugar") if include_advanced else None,
    }
render_food_checker_section(current_food_values, current_food_context, latest_predicted_risk, lang)

st.markdown("---")
st.subheader(t("dataset_preview", lang))
st.dataframe(bundle["dataset_preview"], use_container_width=True)
