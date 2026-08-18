from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.movie import MovieActorAlreadyExistsError, MovieActorNotFoundError
from app.models.actor import Actor
from app.models.movie import Movie
from app.models.movie_actor import MovieActor
from app.schemas.actor import (
    CreateMovieActor,
    MovieCastMember,
    UpdateMovieActor,
)
from app.services.actor.actor import get_actor
from app.services.movie import get_movie

# CREATE


def create_movie_actor(
    movie_id: int, actor_id: int, movie_actor_data: CreateMovieActor, db: Session
) -> MovieActor:
    get_movie(movie_id, db)

    get_actor(actor_id, db)

    movie_actor_exist = db.execute(
        select(MovieActor).where(
            MovieActor.movie_id == movie_id,
            MovieActor.actor_id == actor_id,
        )
    ).scalar_one_or_none()

    if movie_actor_exist is not None:
        raise MovieActorAlreadyExistsError(
            f"Actor with id = {actor_id} is already assigned to movie with id = {movie_id}"
        )

    movie_actor = MovieActor(
        movie_id=movie_id,
        actor_id=actor_id,
        character_name=movie_actor_data.character_name,
    )

    db.add(movie_actor)
    db.commit()
    db.refresh(movie_actor)

    return movie_actor


# READ


def get_movie_actor(movie_id: int, actor_id: int, db: Session) -> MovieActor:
    result = db.execute(
        select(MovieActor).where(
            MovieActor.movie_id == movie_id,
            MovieActor.actor_id == actor_id,
        )
    )

    movie_actor = result.scalar_one_or_none()
    if movie_actor is None:
        raise MovieActorNotFoundError(
            f"Actor with id = {actor_id} is not assigned to movie with id = {movie_id}"
        )

    return movie_actor


def get_movie_actors(
    movie_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[MovieCastMember]:
    get_movie(movie_id, db)

    result = db.execute(
        select(
            Actor.id,
            Actor.name,
            Actor.surname,
            MovieActor.character_name,
        )
        .join(MovieActor, MovieActor.actor_id == Actor.id)
        .where(
            MovieActor.movie_id == movie_id,
            Actor.deleted_at.is_(None),
        )
        .order_by(Actor.id)
        .offset(offset)
        .limit(limit)
    )

    return [MovieCastMember.model_validate(row) for row in result.mappings()]


def get_actor_movies(actor_id: int, db: Session, offset: int = 0, limit: int = 20) -> list[Movie]:
    get_actor(actor_id, db)

    result = db.execute(
        select(Movie)
        .join(MovieActor, MovieActor.movie_id == Movie.id)
        .where(
            MovieActor.actor_id == actor_id,
            Movie.deleted_at.is_(None),
        )
        .order_by(Movie.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# UPDATE


def update_movie_actor(
    movie_id: int, actor_id: int, movie_actor_data: UpdateMovieActor, db: Session
) -> MovieActor:
    movie_actor = get_movie_actor(movie_id, actor_id, db)

    update_data = movie_actor_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(movie_actor, field, value)

    db.commit()
    db.refresh(movie_actor)

    return movie_actor


# DELETE
def delete_movie_actor(movie_id: int, actor_id: int, db: Session) -> None:
    movie_actor = get_movie_actor(movie_id, actor_id, db)

    db.delete(movie_actor)
    db.commit()
