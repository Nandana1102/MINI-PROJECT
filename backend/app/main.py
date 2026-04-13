from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, ensure_schema_upgrade
from .routes.admin import router as admin_router
from .routes.auth import router as auth_router
from .routes.history import router as history_router
from .routes.predict import router as predict_router


Base.metadata.create_all(bind=engine)
ensure_schema_upgrade()

app = FastAPI(
    title="Health Risk Assessment API",
    description="Production-style FastAPI backend for the health risk assessment project.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(history_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "Health Risk Assessment API is live",
        "docs": "/docs",
        "health": "/api/health",
    }
