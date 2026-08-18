import pytest

from app.exceptions.auth import InvalidCredentialsError, RefreshTokenInvalidError
from app.schemas.user import UserCreate
from app.services.auth import login_user, logout_user, refresh_access_token
from app.services.user import create_user, soft_delete_user


def _create_user(db_session):
    return create_user(
        db_session,
        UserCreate(username="user", email="user@test.com", password="password123"),
    )


# login_user


def test_login_user_success(db_session):
    _create_user(db_session)

    tokens = login_user("user", "password123", db_session)

    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"


def test_login_user_invalid_password_raises(db_session):
    _create_user(db_session)

    with pytest.raises(InvalidCredentialsError):
        login_user("user", "wrong-password", db_session)


def test_login_user_unknown_username_raises(db_session):
    with pytest.raises(InvalidCredentialsError):
        login_user("unknown", "password123", db_session)


def test_soft_deleted_user_cannot_login(db_session):
    user = _create_user(db_session)
    soft_delete_user(user.id, db_session)

    with pytest.raises(InvalidCredentialsError):
        login_user("user", "password123", db_session)


# refresh_access_token


def test_refresh_access_token_rotates_refresh_token(db_session):
    _create_user(db_session)
    tokens = login_user("user", "password123", db_session)

    refreshed = refresh_access_token(tokens.refresh_token, db_session)

    assert refreshed.refresh_token != tokens.refresh_token

    with pytest.raises(RefreshTokenInvalidError):
        refresh_access_token(tokens.refresh_token, db_session)


# logout_user


def test_logout_user_revokes_refresh_token(db_session):
    _create_user(db_session)
    tokens = login_user("user", "password123", db_session)

    logout_user(tokens.refresh_token, db_session)

    with pytest.raises(RefreshTokenInvalidError):
        refresh_access_token(tokens.refresh_token, db_session)


def test_invalid_refresh_token_raises(db_session):
    with pytest.raises(RefreshTokenInvalidError):
        refresh_access_token("invalid-token", db_session)
