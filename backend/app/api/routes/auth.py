from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserSession
from app.schemas.auth import LoginRequest, PasswordChange, ProfileUpdate, RegisterRequest, SessionRead, UserRead
from app.security.auth import bearer_scheme, get_current_user, issue_session, token_digest
from app.security.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def _session_response(db: Session, user: User) -> SessionRead:
    token, expires_at = issue_session(db, user)
    db.commit()
    db.refresh(user)
    return SessionRead(access_token=token, expires_at=expires_at, user=user)


@router.post("/register", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> SessionRead:
    if db.scalar(select(User.id).where(User.email == payload.email)) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(full_name=payload.full_name, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.flush()
        result = _session_response(db, user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    return result


@router.post("/login", response_model=SessionRead)
def login(payload: LoginRequest, db: DbSession) -> SessionRead:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.", headers={"WWW-Authenticate": "Bearer"})
    return _session_response(db, user)


@router.get("/me", response_model=UserRead)
def get_profile(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserRead)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession) -> User:
    user.full_name = payload.full_name
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChange, user: CurrentUser, db: DbSession) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    user.password_hash = hash_password(payload.new_password)
    # Invalidate every session so a password change cannot leave stolen sessions active.
    now = datetime.now(timezone.utc)
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({UserSession.revoked_at: now}, synchronize_session=False)
    db.commit()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbSession,
) -> None:
    # Revocation is idempotent; the client should clear its token regardless of response.
    if credentials is None or credentials.scheme.lower() != "bearer":
        return
    session = db.scalar(select(UserSession).where(UserSession.token_hash == token_digest(credentials.credentials)))
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
