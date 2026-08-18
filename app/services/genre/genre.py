from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.genre import GenreAlreadyExistsError, GenreNotFoundError
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.schemas.genre import CreateGenre, UpdateGenre

# CREATE


def create_genre(genre_data: CreateGenre, db: Session) -> Genre:
    genre_exist = db.execute(
        select(Genre).where(Genre.name == genre_data.name)
    ).scalar_one_or_none()

    if genre_exist is not None:
        raise GenreAlreadyExistsError(f"Genre '{genre_data.name}' already exists")

    genre = Genre(
        name=genre_data.name,
    )

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return genre


# READ


def get_genre(genre_id: int, db: Session) -> Genre:
    result = db.execute(select(Genre).where(Genre.id == genre_id))

    genre = result.scalar_one_or_none()
    if genre is None:
        raise GenreNotFoundError(f"Genre with id = {genre_id} not found")

    return genre


def get_genres(db: Session, offset: int = 0, limit: int = 20) -> list[Genre]:
    result = db.execute(select(Genre).order_by(Genre.id).offset(offset).limit(limit))

    return list(result.scalars().all())


def get_genre_movies(genre_id: int, db: Session, offset: int = 0, limit: int = 20) -> list[Movie]:
    get_genre(genre_id, db)

    result = db.execute(
        select(Movie)
        .join(MovieGenre, MovieGenre.movie_id == Movie.id)
        .where(MovieGenre.genre_id == genre_id, Movie.deleted_at.is_(None))
        .order_by(Movie.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# UPDATE


def update_genre(genre_id: int, genre_data: UpdateGenre, db: Session) -> Genre:
    genre = get_genre(genre_id, db)

    update_data = genre_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        genre_exist = db.execute(
            select(Genre).where(
                Genre.id != genre_id,
                Genre.name == update_data["name"],
            )
        ).scalar_one_or_none()

        if genre_exist is not None:
            raise GenreAlreadyExistsError(f"Genre '{update_data['name']}' already exists")

    for field, value in update_data.items():
        setattr(genre, field, value)

    db.commit()
    db.refresh(genre)

    return genre


# DELETE


def delete_genre(genre_id: int, db: Session) -> None:
    genre = get_genre(genre_id, db)

    db.delete(genre)
    db.commit()
