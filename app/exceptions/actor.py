from app.exceptions.base import ConflictError, NotFoundError


class ActorNotFoundError(NotFoundError):
    default_message = "Actor not found"


class ActorAlreadyExistsError(ConflictError):
    default_message = "Actor already exists"
