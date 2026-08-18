from app.exceptions.base import ConflictError, NotFoundError


class MovieNotFoundError(NotFoundError):
    default_message = "Movie not found"


class MovieAlreadyExistsError(ConflictError):
    default_message = "Movie already exists"


class MovieActorNotFoundError(NotFoundError):
    default_message = "This actor is not assigned to this movie"


class MovieActorAlreadyExistsError(ConflictError):
    default_message = "This actor is already assigned to this movie"


class MovieDirectorNotFoundError(NotFoundError):
    default_message = "This director is not assigned to this movie"


class MovieDirectorAlreadyExistsError(ConflictError):
    default_message = "This director is already assigned to this movie"


class MovieGenreNotFoundError(NotFoundError):
    default_message = "This genre is not assigned to this movie"


class MovieGenreAlreadyExistsError(ConflictError):
    default_message = "This genre is already assigned to this movie"
