from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.actor import ActorAlreadyExistsError, ActorNotFoundError
from app.models.actor import Actor
from app.schemas.actor import (
    CreateActor,
    UpdateActor,
)

# CREATE


def create_actor(actor_data: CreateActor, db: Session) -> Actor:
    actor_exist = db.execute(
        select(Actor).where(
            Actor.name == actor_data.name,
            Actor.surname == actor_data.surname,
            Actor.birthdate == actor_data.birthdate,
        )
    ).scalar_one_or_none()

    if actor_exist is not None:
        raise ActorAlreadyExistsError(
            f"Actor '{actor_data.name}' '{actor_data.surname}' already exists"
        )

    actor = Actor(
        name=actor_data.name,
        surname=actor_data.surname,
        birthdate=actor_data.birthdate,
        bio=actor_data.bio,
    )

    db.add(actor)
    db.commit()
    db.refresh(actor)

    return actor


# READ


def get_actor(actor_id: int, db: Session) -> Actor:
    result = db.execute(
        select(Actor).where(
            Actor.id == actor_id,
            Actor.deleted_at.is_(None),
        )
    )

    actor = result.scalar_one_or_none()
    if actor is None:
        raise ActorNotFoundError(f"Actor with id = {actor_id} not found")

    return actor


def get_actor_admin(actor_id: int, db: Session) -> Actor:
    result = db.execute(select(Actor).where(Actor.id == actor_id))

    actor = result.scalar_one_or_none()
    if actor is None:
        raise ActorNotFoundError(f"Actor with id = {actor_id} not found")

    return actor


def get_actors(db: Session, offset: int = 0, limit: int = 20) -> list[Actor]:
    result = db.execute(
        select(Actor)
        .where(Actor.deleted_at.is_(None))
        .order_by(Actor.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


def get_actors_admin(db: Session, offset: int = 0, limit: int = 20) -> list[Actor]:
    result = db.execute(select(Actor).order_by(Actor.id).offset(offset).limit(limit))

    return list(result.scalars().all())


# UPDATE


def update_actor(actor_id: int, actor_data: UpdateActor, db: Session) -> Actor:
    actor = get_actor_admin(actor_id, db)

    update_data = actor_data.model_dump(exclude_unset=True)

    if "name" in update_data or "surname" in update_data or "birthdate" in update_data:
        conflict = db.execute(
            select(Actor).where(
                Actor.id != actor_id,
                Actor.name == update_data.get("name", actor.name),
                Actor.surname == update_data.get("surname", actor.surname),
                Actor.birthdate == update_data.get("birthdate", actor.birthdate),
            )
        ).scalar_one_or_none()

        if conflict is not None:
            raise ActorAlreadyExistsError(
                f"Actor '{update_data.get('name', actor.name)}' "
                f"'{update_data.get('surname', actor.surname)}' already exists"
            )

    for field, value in update_data.items():
        setattr(actor, field, value)

    db.commit()
    db.refresh(actor)

    return actor


def restore_actor(actor_id: int, db: Session) -> Actor:
    actor = get_actor_admin(actor_id, db)

    actor.deleted_at = None

    db.commit()
    db.refresh(actor)

    return actor


# DELETE


def soft_delete_actor(actor_id: int, db: Session) -> Actor:
    actor = get_actor(actor_id, db)

    actor.deleted_at = datetime.now(UTC)

    db.commit()
    db.refresh(actor)

    return actor
