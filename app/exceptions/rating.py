from app.exceptions.base import ConflictError, NotFoundError


class RatingNotFoundError(NotFoundError):
    default_message = "Rating not found"


class RatingAlreadyExistsError(ConflictError):
    default_message = "You have already rated this movie"
