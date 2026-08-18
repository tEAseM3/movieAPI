from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.movie import MovieAlreadyExistsError, MovieNotFoundError
from app.models.movie import Movie
from app.schemas.movie import CreateMovie, UpdateMovie
from app.services.language import get_language

# CREATE


def create_movie(movie_data: CreateMovie, db: Session) -> Movie:
    get_language(movie_data.language_id, db)

    movie_exist = db.execute(
        select(Movie).where(
            Movie.title == movie_data.title,
            Movie.release_date == movie_data.release_date,
        )
    ).scalar_one_or_none()

    if movie_exist is not None:
        raise MovieAlreadyExistsError(f"Movie '{movie_data.title}' already exists")

    movie = Movie(
        language_id=movie_data.language_id,
        title=movie_data.title,
        description=movie_data.description,
        release_date=movie_data.release_date,
        duration_time=movie_data.duration_time,
    )

    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie


# READ


def get_movie(movie_id: int, db: Session) -> Movie:
    result = db.execute(
        select(Movie).where(
            Movie.id == movie_id,
            Movie.deleted_at.is_(None),
        )
    )

    movie = result.scalar_one_or_none()

    if movie is None:
        raise MovieNotFoundError(f"Movie with id = {movie_id} not found")

    return movie


def get_movie_admin(movie_id: int, db: Session) -> Movie:
    result = db.execute(select(Movie).where(Movie.id == movie_id))

    movie = result.scalar_one_or_none()

    if movie is None:
        raise MovieNotFoundError(f"Movie with id = {movie_id} not found")

    return movie


def get_movie_by_title(
    movie_title: str, db: Session, offset: int = 0, limit: int = 20
) -> list[Movie]:
    result = db.execute(
        select(Movie)
        .where(Movie.title.ilike(f"%{movie_title}%"), Movie.deleted_at.is_(None))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


def get_movies(db: Session, offset: int = 0, limit: int = 20) -> list[Movie]:
    result = db.execute(
        select(Movie)
        .where(Movie.deleted_at.is_(None))
        .order_by(Movie.id)
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


def get_movies_admin(db: Session, offset: int = 0, limit: int = 20) -> list[Movie]:
    result = db.execute(select(Movie).order_by(Movie.id).offset(offset).limit(limit))

    return list(result.scalars().all())


# UPDATE


def update_movie(movie_id: int, movie_data: UpdateMovie, db: Session) -> Movie:
    movie = get_movie_admin(movie_id, db)

    update_data = movie_data.model_dump(
        exclude_unset=True,
    )

    if "language_id" in update_data:
        get_language(update_data["language_id"], db)

    if "title" in update_data or "release_date" in update_data:
        movie_exist = db.execute(
            select(Movie).where(
                Movie.id != movie_id,
                Movie.title == update_data.get("title", movie.title),
                Movie.release_date == update_data.get("release_date", movie.release_date),
            )
        ).scalar_one_or_none()

        if movie_exist is not None:
            raise MovieAlreadyExistsError(
                f"Movie '{update_data.get('title', movie.title)}' already exists"
            )

    for field, value in update_data.items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)

    return movie


def restore_movie(movie_id: int, db: Session) -> Movie:
    movie = get_movie_admin(movie_id, db)

    movie.deleted_at = None

    db.commit()
    db.refresh(movie)

    return movie


# DELETE


def soft_delete_movie(movie_id: int, db: Session) -> Movie:
    movie = get_movie(movie_id, db)

    movie.deleted_at = datetime.now(UTC)

    db.commit()
    db.refresh(movie)

    return movie
