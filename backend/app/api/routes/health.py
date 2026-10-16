from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

router = APIRouter()


@router.get("/live", summary="Liveness check")
def liveness() -> dict[str, str]:
    """Confirm that the API process is responding; does not require the database."""
    return {"status": "ok", "service": "ledgermind-api"}


@router.get("/ready", summary="Readiness check")
def readiness() -> dict[str, str]:
    """Confirm that the API can reach its configured database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready. Check DATABASE_URL and PostgreSQL availability.",
        ) from exc
    return {"status": "ready", "database": "connected"}
