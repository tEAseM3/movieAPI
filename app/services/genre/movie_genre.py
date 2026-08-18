from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.movie import MovieGenreAlreadyExistsError, MovieGenreNotFoundError
from app.models.genre import Genre
from app.models.movie_genre import MovieGenre
from app.services.genre.genre import get_genre
from app.services.movie import get_movie

# CREATE


def create_movie_genre(movie_id: int, genre_id: int, db: Session) -> MovieGenre:
    get_movie(movie_id, db)
    get_genre(genre_id, db)

    movie_genre_exist = db.execute(
        select(MovieGenre).where(
            MovieGenre.movie_id == movie_id,
            MovieGenre.genre_id == genre_id,
        )
    ).scalar_one_or_none()

    if movie_genre_exist is not None:
        raise MovieGenreAlreadyExistsError(
            f"Genre with id = {genre_id} is already assigned to movie with id = {movie_id}"
        )

    movie_genre = MovieGenre(
        movie_id=movie_id,
        genre_id=genre_id,
    )

    db.add(movie_genre)
    db.commit()
    db.refresh(movie_genre)

    return movie_genre


# READ


def get_movie_genre(movie_id: int, genre_id: int, db: Session) -> MovieGenre:
    result = db.execute(
        select(MovieGenre).where(
            MovieGenre.movie_id == movie_id,
            MovieGenre.genre_id == genre_id,
        )
    )

    movie_genre = result.scalar_one_or_none()

    if movie_genre is None:
        raise MovieGenreNotFoundError(
            f"Genre with id = {genre_id} is not assigned to movie id = {movie_id}"
        )

    return movie_genre


def get_movie_genres(movie_id: int, db: Session, offset: int = 0, limit: int = 20) -> list[Genre]:
    get_movie(movie_id, db)

    result = db.execute(
        select(Genre)
        .join(MovieGenre, MovieGenre.genre_id == Genre.id)
        .where(MovieGenre.movie_id == movie_id)
        .order_by(Genre.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# DELETE


def delete_movie_genre(movie_id: int, genre_id: int, db: Session) -> None:
    movie_genre = get_movie_genre(movie_id, genre_id, db)

    db.delete(movie_genre)
    db.commit()
