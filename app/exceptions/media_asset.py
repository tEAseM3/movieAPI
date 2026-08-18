from app.exceptions.base import ConflictError, NotFoundError


class MediaAssetNotFoundError(NotFoundError):
    default_message = "Media asset not found"


class MediaAssetAlreadyExistsError(ConflictError):
    default_message = "Media asset already exists"
