from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions.rating import RatingAlreadyExistsError, RatingNotFoundError
from app.models.rating import Rating
from app.schemas.rating import CreateRating, UpdateRating
from app.services.movie import get_movie

# CREATE


def create_rating(movie_id: int, user_id: int, rating_data: CreateRating, db: Session) -> Rating:
    get_movie(movie_id, db)

    rating_exist = db.execute(
        select(Rating).where(
            Rating.movie_id == movie_id,
            Rating.user_id == user_id,
        )
    ).scalar_one_or_none()

    if rating_exist is not None:
        raise RatingAlreadyExistsError(
            f"User with id = {user_id} has already rated movie with id = {movie_id}"
        )

    rating = Rating(
        movie_id=movie_id,
        user_id=user_id,
        rating=rating_data.rating,
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    return rating


# READ


def get_rating(rating_id: int, db: Session) -> Rating:
    result = db.execute(select(Rating).where(Rating.id == rating_id))

    rating = result.scalar_one_or_none()
    if rating is None:
        raise RatingNotFoundError(f"Rating with id = {rating_id} not found")

    return rating


def get_movie_rating(movie_id: int, db: Session) -> tuple[float, int]:
    get_movie(movie_id, db)

    result = db.execute(
        select(
            func.avg(Rating.rating),
            func.count(Rating.id),
        ).where(Rating.movie_id == movie_id)
    )

    avg_rating, ratings_count = result.one()

    return (
        float(avg_rating) if avg_rating is not None else 0.0,
        ratings_count,
    )


# UPDATE


def update_rating(movie_id: int, user_id: int, rating_data: UpdateRating, db: Session) -> Rating:
    result = db.execute(
        select(Rating).where(
            Rating.movie_id == movie_id,
            Rating.user_id == user_id,
        )
    )

    rating = result.scalar_one_or_none()
    if rating is None:
        raise RatingNotFoundError(
            f"Rating by user id = {user_id} for movie id = {movie_id} not found"
        )

    update_data = rating_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rating, field, value)

    db.commit()
    db.refresh(rating)

    return rating


# DELETE


def delete_rating(movie_id: int, user_id: int, db: Session) -> None:
    result = db.execute(
        select(Rating).where(
            Rating.movie_id == movie_id,
            Rating.user_id == user_id,
        )
    )

    rating = result.scalar_one_or_none()
    if rating is None:
        raise RatingNotFoundError(
            f"Rating by user id = {user_id} for movie id = {movie_id} not found"
        )

    db.delete(rating)
    db.commit()
