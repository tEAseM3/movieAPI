from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.movie import (
    MovieDirectorAlreadyExistsError,
    MovieDirectorNotFoundError,
)
from app.models.director import Director
from app.models.movie import Movie
from app.models.movie_director import MovieDirector
from app.services.director.director import get_director
from app.services.movie import get_movie

# CREATE


def create_movie_director(movie_id: int, director_id: int, db: Session) -> MovieDirector:
    get_movie(movie_id, db)

    get_director(director_id, db)

    movie_director_exist = db.execute(
        select(MovieDirector).where(
            MovieDirector.movie_id == movie_id,
            MovieDirector.director_id == director_id,
        )
    ).scalar_one_or_none()

    if movie_director_exist is not None:
        raise MovieDirectorAlreadyExistsError(
            f"Director with id = {director_id} is already assigned to movie with id = {movie_id}"
        )

    movie_director = MovieDirector(
        movie_id=movie_id,
        director_id=director_id,
    )

    db.add(movie_director)
    db.commit()
    db.refresh(movie_director)

    return movie_director


# READ


def get_movie_director(movie_id: int, director_id: int, db: Session) -> MovieDirector:
    result = db.execute(
        select(MovieDirector).where(
            MovieDirector.movie_id == movie_id,
            MovieDirector.director_id == director_id,
        )
    )

    movie_director = result.scalar_one_or_none()

    if movie_director is None:
        raise MovieDirectorNotFoundError(
            f"Director wiwth id = {director_id} is not assigned to movie with id = {movie_id}"
        )

    return movie_director


def get_movie_directors(
    movie_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[Director]:
    get_movie(movie_id, db)

    result = db.execute(
        select(Director)
        .join(MovieDirector, MovieDirector.director_id == Director.id)
        .where(
            MovieDirector.movie_id == movie_id,
            Director.deleted_at.is_(None),
        )
        .order_by(Director.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


def get_director_movies(
    director_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[Movie]:
    get_director(director_id, db)

    result = db.execute(
        select(Movie)
        .join(MovieDirector, MovieDirector.movie_id == Movie.id)
        .where(
            MovieDirector.director_id == director_id,
            Movie.deleted_at.is_(None),
        )
        .order_by(Movie.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# DELETE


def delete_movie_director(movie_id: int, director_id: int, db: Session) -> None:
    movie_director = get_movie_director(movie_id, director_id, db)

    db.delete(movie_director)
    db.commit()
