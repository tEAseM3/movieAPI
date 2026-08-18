# app/exceptions/refresh_token.py
from app.exceptions.base import UnauthorizedError


class RefreshTokenInvalidError(UnauthorizedError):
    default_message = "Invalid or expired refresh token"


class InvalidCredentialsError(UnauthorizedError):
    default_message = "Invalid username or password"
