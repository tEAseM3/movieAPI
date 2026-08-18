from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.favorite import FavoriteAlreadyExistsError, FavoriteNotFoundError
from app.models.favorite import Favorite
from app.schemas.favorite import CreateFavorite
from app.services.movie import get_movie

# CREATE


def create_favorite(
    movie_id: int, user_id: int, favorite_data: CreateFavorite, db: Session
) -> Favorite:

    get_movie(movie_id, db)

    favorite_exist = db.execute(
        select(Favorite).where(
            Favorite.movie_id == movie_id,
            Favorite.user_id == user_id,
        )
    ).scalar_one_or_none()

    if favorite_exist is not None:
        raise FavoriteAlreadyExistsError(
            f"Movie with id = {movie_id} is already in favorites for user with id = {user_id}"
        )

    favorite = Favorite(
        movie_id=movie_id,
        user_id=user_id,
        content=favorite_data.content,
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


# READ


def get_favorite(favorite_id: int, db: Session) -> Favorite:
    result = db.execute(select(Favorite).where(Favorite.id == favorite_id))

    favorite = result.scalar_one_or_none()
    if favorite is None:
        raise FavoriteNotFoundError(f"Favorite with id = {favorite_id} not found")

    return favorite


def get_favorites_by_user(
    user_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[Favorite]:
    result = db.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# DELETE


def delete_favorite(movie_id: int, user_id: int, db: Session) -> None:
    favorite = db.execute(
        select(Favorite).where(
            Favorite.movie_id == movie_id,
            Favorite.user_id == user_id,
        )
    ).scalar_one_or_none()

    if favorite is None:
        raise FavoriteNotFoundError(
            f"Movie with id = {movie_id} is not in favorites for user with id = {user_id}"
        )

    db.delete(favorite)
    db.commit()
