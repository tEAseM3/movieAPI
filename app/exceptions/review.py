from app.exceptions.base import ConflictError, ForbiddenError, NotFoundError


class ReviewNotFoundError(NotFoundError):
    default_message = "Review not found"


class ReviewAlreadyExistsError(ConflictError):
    default_message = "You have already reviewed this movie"


class ReviewPermissionError(ForbiddenError):
    default_message = "You do not have permission to modify this review"
