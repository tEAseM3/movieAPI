from app.exceptions.base import ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    default_message = "User not found"


class UserAlreadyExistsError(ConflictError):
    default_message = "User already exists"


class CannotModifyOwnRoleError(ConflictError):
    default_message = "Cannot change your own role"
