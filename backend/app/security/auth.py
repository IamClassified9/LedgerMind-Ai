from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business
from app.models.user import BusinessMembership, User, UserSession

SESSION_DAYS = 7
bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_session(db: Session, user: User) -> tuple[str, datetime]:
    raw_token = secrets.token_urlsafe(40)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    db.add(UserSession(user_id=user.id, token_hash=token_digest(raw_token), expires_at=expires_at))
    return raw_token, expires_at


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbSession,
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == token_digest(credentials.credentials),
            UserSession.revoked_at.is_(None),
        )
    )
    if session is None:
        raise unauthorized
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires <= datetime.now(timezone.utc):
        raise unauthorized
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


def require_business_access(db: Session, user: User, business_id: UUID) -> Business:
    business = db.scalar(
        select(Business)
        .join(BusinessMembership, BusinessMembership.business_id == Business.id)
        .where(Business.id == business_id, BusinessMembership.user_id == user.id)
    )
    # Use 404 for both nonexistent and inaccessible businesses to avoid leaking IDs.
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found.")
    return business


