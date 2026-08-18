from app.exceptions.base import ConflictError, NotFoundError


class DirectorNotFoundError(NotFoundError):
    default_message = "Director not found"


class DirectorAlreadyExistsError(ConflictError):
    default_message = "Director already exists"
