from app.exceptions.base import ConflictError, NotFoundError


class LanguageNotFoundError(NotFoundError):
    default_message = "Language not found"


class LanguageAlreadyExistsError(ConflictError):
    default_message = "Language already exists"


class LanguageInUseError(ConflictError):
    default_message = "Language is in use and cannot be deleted"
