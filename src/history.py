from __future__ import annotations

from datetime import datetime
from typing import Dict

import pandas as pd

from .utils import DATA_DIR


HISTORY_FILE = DATA_DIR / "prediction_history.csv"


def append_prediction_history(record: Dict[str, object]) -> None:
    payload = dict(record)
    payload.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    history_row = pd.DataFrame([payload])
    history_row.to_csv(HISTORY_FILE, mode="a", header=not HISTORY_FILE.exists(), index=False)


def load_prediction_history() -> pd.DataFrame:
    if not HISTORY_FILE.exists():
        return pd.DataFrame()
    history_df = pd.read_csv(HISTORY_FILE)
    if "timestamp" in history_df.columns:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
        history_df = history_df.sort_values(by="timestamp")
    return history_df
