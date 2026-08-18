from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.review import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
    ReviewPermissionError,
)
from app.models.review import Review
from app.schemas.review import CreateReview, UpdateReview
from app.services.movie import get_movie

# CREATE


def create_review(movie_id: int, user_id: int, review_data: CreateReview, db: Session) -> Review:
    get_movie(movie_id, db)

    review_exist = db.execute(
        select(Review).where(
            Review.movie_id == movie_id,
            Review.user_id == user_id,
        )
    ).scalar_one_or_none()

    if review_exist is not None:
        raise ReviewAlreadyExistsError(
            f"User with id = {user_id} has already reviewed movie with id = {movie_id}"
        )

    review = Review(
        movie_id=movie_id,
        user_id=user_id,
        content=review_data.content,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


# READ


def get_review(review_id: int, db: Session) -> Review:
    result = db.execute(select(Review).where(Review.id == review_id))

    review = result.scalar_one_or_none()

    if review is None:
        raise ReviewNotFoundError(f"Review with id = {review_id} not found")

    return review


def get_reviews(movie_id: int, db: Session, offset: int = 0, limit: int = 20) -> list[Review]:
    get_movie(movie_id, db)

    result = db.execute(
        select(Review)
        .where(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


def get_reviews_admin(db: Session, offset: int = 0, limit: int = 20) -> list[Review]:
    result = db.execute(
        select(Review).order_by(Review.created_at.desc()).offset(offset).limit(limit)
    )

    return result.scalars().all()


# UPDATE


def update_review(review_id: int, user_id: int, review_data: UpdateReview, db: Session) -> Review:
    review = get_review(review_id, db)

    if review.user_id != user_id:
        raise ReviewPermissionError("You can only update your own review")

    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)

    return review


# DELETE


def delete_review(review_id: int, user_id: int, db: Session) -> None:
    review = get_review(review_id, db)

    if review.user_id != user_id:
        raise ReviewPermissionError("You can only delete your own review")

    db.delete(review)
    db.commit()


def delete_review_admin(review_id: int, db: Session) -> None:
    review = get_review(review_id, db)

    db.delete(review)
    db.commit()
