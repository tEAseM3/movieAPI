from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.review import CreateReview, DisplayReview, UpdateReview
from app.services.review import (
    create_review,
    delete_review,
    get_review,
    get_reviews,
    update_review,
)

router = APIRouter(tags=["Reviews"])


# POST
@router.post("/movies/{movie_id}/reviews", response_model=DisplayReview)
def create_review_endpoint(
    movie_id: int,
    review: CreateReview,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return create_review(movie_id, current_user.id, review, db)


# GET


@router.get("/movies/{movie_id}/reviews", response_model=list[DisplayReview])
def get_reviews_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_reviews(movie_id, db, offset, page_size)


@router.get("/reviews/{review_id}", response_model=DisplayReview)
def get_review_endpoint(review_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_review(review_id, db)


# PATCH


@router.patch("/reviews/{review_id}", response_model=DisplayReview)
def update_review_endpoint(
    review_id: int,
    review_data: UpdateReview,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return update_review(review_id, current_user.id, review_data, db)


# DELETE


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review_endpoint(
    review_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    delete_review(review_id, current_user.id, db)
