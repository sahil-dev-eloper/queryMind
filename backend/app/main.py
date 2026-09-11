from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.databases import router as databases_router
from app.api.queries import conversation_router, router as queries_router
from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()
app = FastAPI(title="QueryMind API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(databases_router, prefix="/api")
app.include_router(queries_router, prefix="/api")
app.include_router(conversation_router, prefix="/api")


from app.db.session import SessionLocal
from app.services.demo_database import ensure_demo_database


@app.on_event("startup")
def on_startup() -> None:
    try:
        with SessionLocal() as db:
            ensure_demo_database(db)
    except Exception:
        pass


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"name": "QueryMind API", "status": "ok"}
