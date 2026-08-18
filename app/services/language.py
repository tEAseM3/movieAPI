from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.language import (
    LanguageAlreadyExistsError,
    LanguageInUseError,
    LanguageNotFoundError,
)
from app.models.language import Language
from app.models.movie import Movie
from app.schemas.language import CreateLanguage, UpdateLanguage

# CREATE


def create_language(language_data: CreateLanguage, db: Session) -> Language:
    language_exist = db.execute(
        select(Language).where(
            (Language.name == language_data.name) | (Language.code == language_data.code)
        )
    ).scalar_one_or_none()

    if language_exist is not None:
        raise LanguageAlreadyExistsError(
            f"Language '{language_data.name}' ({language_data.code}) already exists"
        )

    language = Language(
        name=language_data.name,
        code=language_data.code,
    )

    db.add(language)
    db.commit()
    db.refresh(language)

    return language


# READ


def get_language(language_id: int, db: Session) -> Language:
    result = db.execute(select(Language).where(Language.id == language_id))

    language = result.scalar_one_or_none()
    if language is None:
        raise LanguageNotFoundError(f"Language with id = {language_id} not found")

    return language


def get_languages(db: Session, offset: int = 0, limit: int = 20) -> list[Language]:
    result = db.execute(select(Language).order_by(Language.id).offset(offset).limit(limit))

    return list(result.scalars().all())


def get_language_movies(
    language_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[Movie]:
    get_language(language_id, db)

    result = db.execute(
        select(Movie)
        .where(Movie.language_id == language_id, Movie.deleted_at.is_(None))
        .order_by(Movie.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# UPDATE


def update_language(language_id: int, language_data: UpdateLanguage, db: Session) -> Language:
    language = get_language(language_id, db)

    update_data = language_data.model_dump(exclude_unset=True)

    if "name" in update_data or "code" in update_data:
        language_conflict = db.execute(
            select(Language).where(
                Language.id != language_id,
                (Language.name == update_data.get("name", language.name))
                | (Language.code == update_data.get("code", language.code)),
            )
        ).scalar_one_or_none()

        if language_conflict is not None:
            raise LanguageAlreadyExistsError(
                f"Language with name = '{update_data.get('name', language.name)}' "
                f"or code = '{update_data.get('code', language.code)}' already exists"
            )

    for field, value in update_data.items():
        setattr(language, field, value)

    db.commit()
    db.refresh(language)

    return language


# DELETE


def delete_language(language_id: int, db: Session) -> None:
    language = get_language(language_id, db)

    language_in_use_exist = db.execute(
        select(Movie).where(Movie.language_id == language_id)
    ).first()

    if language_in_use_exist is not None:
        raise LanguageInUseError(
            f"Language with id = {language_id} is in use and cannot be deleted"
        )

    db.delete(language)
    db.commit()
