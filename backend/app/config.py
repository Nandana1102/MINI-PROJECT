from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'backend' / 'health_risk_dev.db').as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-for-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
