from app.exceptions.base import ConflictError, NotFoundError


class GenreNotFoundError(NotFoundError):
    default_message = "Genre not found"


class GenreAlreadyExistsError(ConflictError):
    default_message = "Genre already exists"
