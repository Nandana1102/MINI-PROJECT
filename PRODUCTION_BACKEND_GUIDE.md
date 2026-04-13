# Production Backend Guide (FastAPI + PostgreSQL)

## Current Progress
The project has been upgraded with a production-style backend under `backend/`.

### Implemented Phases
- **Phase 1:** FastAPI backend structure with user roles (`user` / `admin`)
- **Phase 2:** PostgreSQL-ready database layer using SQLAlchemy
- **Phase 3:** Authentication + prediction + history APIs
- **Phase 4:** Streamlit frontend connected to backend APIs

### Current Admin Progress
- **Phase 5:** Admin-only APIs implemented
- **Next Phase:** Login-first dashboard flow with admin dashboard UI

## Backend Folder
```text
backend/
│-- app/
│   │-- main.py
│   │-- config.py
│   │-- database.py
│   │-- models.py
│   │-- schemas.py
│   │-- security.py
│   │-- dependencies.py
│   │-- routes/
│   │   │-- auth.py
│   │   │-- predict.py
│   │   │-- history.py
│   │-- services/
│   │   │-- ml_service.py
│-- requirements.txt
```

## PostgreSQL Setup
Create a PostgreSQL database, then set:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/health_risk_db
SECRET_KEY=replace-with-a-strong-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

You can copy values from `.env.example`.

## Install Backend Dependencies
```bash
cd C:\Users\nanda\health_risk_project
python -m pip install -r backend/requirements.txt
```

## Run the FastAPI Backend
```bash
cd C:\Users\nanda\health_risk_project
uvicorn backend.app.main:app --reload
```

## Swagger API Docs
Open:
- `http://127.0.0.1:8000/docs`

## Available APIs
### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `PUT /api/auth/preferences/language`

`/api/auth/me` now returns the logged-in user's role and preferred language.

### Prediction
- `GET /api/health`
- `POST /api/predict`

### History
- `GET /api/history/me`

### Admin
- `GET /api/admin/stats`
- `GET /api/admin/users`
- `GET /api/admin/predictions`

These endpoints are protected and require an authenticated user with role `admin`.

## Tested Local Flow
1. Register user
2. Login user
3. Use bearer token
4. Call prediction API
5. Retrieve prediction history
6. Update preferred language and verify `/api/auth/me`

## Create an Admin User
Normal registration creates users with role `user`.
To create an admin account, run:

```bash
cd C:\Users\nanda\health_risk_project
python backend/create_admin.py
```

Then enter admin username, email, and password.

## Important Note
If `DATABASE_URL` is not set, the backend falls back to SQLite for local development testing. For production deployment, use PostgreSQL.
