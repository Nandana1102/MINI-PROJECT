from __future__ import annotations

import sys
from getpass import getpass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import Base, SessionLocal, engine, ensure_schema_upgrade
from backend.app.models import User
from backend.app.security import get_password_hash


def main() -> None:
    print("Create Admin User")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ").strip()
    preferred_language = input("Preferred language [en/hi] (default: en): ").strip().lower() or "en"

    if not username or not email or len(password) < 6:
        print("Invalid input. Username/email required and password must be at least 6 characters.")
        return
    if preferred_language not in {"en", "hi"}:
        print("Invalid language. Use 'en' or 'hi'.")
        return

    Base.metadata.create_all(bind=engine)
    ensure_schema_upgrade()

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            print("User with this email or username already exists.")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role="admin",
            preferred_language=preferred_language,
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
