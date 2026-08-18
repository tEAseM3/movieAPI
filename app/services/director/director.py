from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.director import DirectorAlreadyExistsError, DirectorNotFoundError
from app.models.director import Director
from app.schemas.director import (
    CreateDirector,
    UpdateDirector,
)

# CREATE


def create_director(director_data: CreateDirector, db: Session) -> Director:
    director_exist = db.execute(
        select(Director).where(
            Director.name == director_data.name,
            Director.surname == director_data.surname,
            Director.birthdate == director_data.birthdate,
        )
    ).scalar_one_or_none()

    if director_exist is not None:
        raise DirectorAlreadyExistsError(
            f"Director '{director_data.name}' '{director_data.surname}' already exists"
        )

    director = Director(
        name=director_data.name,
        surname=director_data.surname,
        birthdate=director_data.birthdate,
        bio=director_data.bio,
    )

    db.add(director)
    db.commit()
    db.refresh(director)

    return director


# READ


def get_director(director_id: int, db: Session) -> Director:
    result = db.execute(
        select(Director).where(
            Director.id == director_id,
            Director.deleted_at.is_(None),
        )
    )

    director = result.scalar_one_or_none()

    if director is None:
        raise DirectorNotFoundError(f"Director with id = {director_id} not found")

    return director


def get_director_admin(director_id: int, db: Session) -> Director:
    result = db.execute(select(Director).where(Director.id == director_id))

    director = result.scalar_one_or_none()

    if director is None:
        raise DirectorNotFoundError(f"Director with id = {director_id} not found")

    return director


def get_directors(db: Session, offset: int = 0, limit: int = 20) -> list[Director]:
    result = db.execute(
        select(Director)
        .where(Director.deleted_at.is_(None))
        .order_by(Director.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


def get_directors_admin(db: Session, offset: int = 0, limit: int = 20) -> list[Director]:
    result = db.execute(select(Director).order_by(Director.id).offset(offset).limit(limit))

    return list(result.scalars().all())


# UPDATE


def update_director(director_id: int, director_data: UpdateDirector, db: Session) -> Director:
    director = get_director_admin(director_id, db)

    update_data = director_data.model_dump(exclude_unset=True)

    if "name" in update_data or "surname" in update_data or "birthdate" in update_data:
        conflict = db.execute(
            select(Director).where(
                Director.id != director_id,
                Director.name == update_data.get("name", director.name),
                Director.surname == update_data.get("surname", director.surname),
                Director.birthdate == update_data.get("birthdate", director.birthdate),
            )
        ).scalar_one_or_none()

        if conflict is not None:
            raise DirectorAlreadyExistsError(
                f"Director '{update_data.get('name', director.name)}' "
                f"'{update_data.get('surname', director.surname)}' already exists"
            )

    for field, value in update_data.items():
        setattr(director, field, value)

    db.commit()
    db.refresh(director)

    return director


def restore_director(director_id: int, db: Session) -> Director:
    director = get_director_admin(director_id, db)

    director.deleted_at = None

    db.commit()
    db.refresh(director)

    return director


# DELETE


def soft_delete_director(director_id: int, db: Session) -> Director:
    director = get_director(director_id, db)

    director.deleted_at = datetime.now(UTC)

    db.commit()
    db.refresh(director)

    return director
