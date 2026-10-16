from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

if settings.sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.2,
        send_default_pii=False,
        enable_logs=True,
    )

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Backend foundation for LedgerMind AI, a configurable business-record "
        "platform initially supporting restaurants and supermarkets."
    ),
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["service"], include_in_schema=False)
def root() -> dict[str, str]:
    """Return a small service-identification response."""
    return {"service": settings.app_name, "status": "running"}
