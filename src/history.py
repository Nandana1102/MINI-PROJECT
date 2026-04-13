from __future__ import annotations

import csv
from datetime import datetime
from typing import Dict, List

import pandas as pd

from .utils import DATA_DIR


HISTORY_FILE = DATA_DIR / "prediction_history.csv"
HISTORY_COLUMNS = [
    "model_name",
    "age",
    "gender",
    "diet_score",
    "sleep_hours",
    "activity_level",
    "bmi",
    "bmi_category",
    "hrs_score",
    "predicted_risk",
    "advanced_parameters_used",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "blood_sugar",
    "smoking_habit",
    "screen_time_hours",
    "stress_level",
    "timestamp",
]


def _read_history_rows() -> List[Dict[str, object]]:
    if not HISTORY_FILE.exists():
        return []

    rows: List[Dict[str, object]] = []
    with HISTORY_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        all_rows = list(reader)

    if not all_rows:
        return []

    header = list(all_rows[0])
    if "advanced_parameters_used" not in header:
        try:
            insert_index = header.index("predicted_risk") + 1
        except ValueError:
            insert_index = 10
        if any(len(row) == len(header) + 1 for row in all_rows[1:]):
            header = header[:insert_index] + ["advanced_parameters_used"] + header[insert_index:]

    for row in all_rows[1:]:
        if not any(str(cell).strip() for cell in row):
            continue

        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[: len(header)]

        mapped = dict(zip(header, row))
        normalized = {column: mapped.get(column, "") for column in HISTORY_COLUMNS}
        rows.append(normalized)

    return rows


def _repair_shifted_row(row: Dict[str, object]) -> Dict[str, object]:
    advanced_value = str(row.get("advanced_parameters_used", "")).strip()
    timestamp_value = str(row.get("timestamp", "")).strip()
    valid_boolean_tokens = {"", "True", "False", "0", "1", "true", "false"}

    if advanced_value not in valid_boolean_tokens and not timestamp_value:
        return {
            **row,
            "timestamp": row.get("stress_level", ""),
            "stress_level": row.get("screen_time_hours", ""),
            "screen_time_hours": row.get("smoking_habit", ""),
            "smoking_habit": row.get("blood_sugar", ""),
            "blood_sugar": row.get("blood_pressure_diastolic", ""),
            "blood_pressure_diastolic": row.get("blood_pressure_systolic", ""),
            "blood_pressure_systolic": row.get("advanced_parameters_used", ""),
            "advanced_parameters_used": False,
        }
    return row


def load_prediction_history() -> pd.DataFrame:
    rows = [_repair_shifted_row(row) for row in _read_history_rows()]
    if not rows:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    history_df = pd.DataFrame(rows, columns=HISTORY_COLUMNS)

    numeric_columns = [
        "age",
        "diet_score",
        "sleep_hours",
        "activity_level",
        "bmi",
        "hrs_score",
        "blood_pressure_systolic",
        "blood_pressure_diastolic",
        "blood_sugar",
        "screen_time_hours",
        "stress_level",
    ]
    for column in numeric_columns:
        history_df[column] = pd.to_numeric(history_df[column], errors="coerce")

    if "advanced_parameters_used" in history_df.columns:
        history_df["advanced_parameters_used"] = history_df["advanced_parameters_used"].replace({"": pd.NA})

    if "timestamp" in history_df.columns:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
        history_df = history_df.sort_values(by="timestamp", na_position="last")

    return history_df


def append_prediction_history(record: Dict[str, object]) -> None:
    payload = {column: record.get(column, "") for column in HISTORY_COLUMNS}
    payload["timestamp"] = payload.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing_df = load_prediction_history()
    new_row_df = pd.DataFrame([payload], columns=HISTORY_COLUMNS)
    updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
    updated_df.to_csv(HISTORY_FILE, index=False)
