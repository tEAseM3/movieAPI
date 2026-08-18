from app.exceptions.base import ConflictError, NotFoundError


class FavoriteNotFoundError(NotFoundError):
    default_message = "Favorite not found"


class FavoriteAlreadyExistsError(ConflictError):
    default_message = "Movie is already in favorites"
