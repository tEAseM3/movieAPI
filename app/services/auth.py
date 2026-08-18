from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    verify_password,
)
from app.exceptions.auth import InvalidCredentialsError, RefreshTokenInvalidError
from app.models.refresh_token import RefreshToken
from app.schemas.auth import TokenResponse
from app.services.user import get_user_by_username


def login_user(username: str, password: str, db: Session) -> TokenResponse:
    user = get_user_by_username(username, db)

    if user is None:
        raise InvalidCredentialsError()

    if user.deleted_at is not None:
        raise InvalidCredentialsError()

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = _create_and_store_refresh_token(user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
    stored = _validate_refresh_token(refresh_token, db)

    new_access_token = create_access_token({"sub": str(stored.user_id)})

    _revoke_refresh_token(stored, db)
    new_refresh_token = _create_and_store_refresh_token(stored.user_id, db)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


def logout_user(refresh_token: str, db: Session) -> None:
    stored = _validate_refresh_token(refresh_token, db)
    _revoke_refresh_token(stored, db)


def _create_and_store_refresh_token(user_id: int, db: Session) -> str:
    token = create_refresh_token()

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=get_refresh_token_expiry(),
    )

    db.add(refresh_token)
    db.commit()

    return token


def _validate_refresh_token(token: str, db: Session) -> RefreshToken:
    result = db.execute(select(RefreshToken).where(RefreshToken.token == token))
    stored = result.scalar_one_or_none()

    if stored is None or stored.revoked or stored.expires_at < datetime.now(UTC):
        raise RefreshTokenInvalidError()

    return stored


def _revoke_refresh_token(stored: RefreshToken, db: Session) -> None:
    stored.revoked = True
    db.commit()
