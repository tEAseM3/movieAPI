from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.rating import CreateRating, DisplayRating, MovieRating, UpdateRating
from app.services.rating import (
    create_rating,
    delete_rating,
    get_movie_rating,
    update_rating,
)

router = APIRouter(tags=["Ratings"])

# POST


@router.post("/movies/{movie_id}/rating", response_model=DisplayRating, status_code=201)
def create_rating_endpoint(
    movie_id: int,
    rating_data: CreateRating,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return create_rating(movie_id, current_user.id, rating_data, db)


# GET


@router.get("/movies/{movie_id}/rating", response_model=MovieRating)
def get_movie_rating_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    average_rating, ratings_count = get_movie_rating(movie_id, db)

    return {
        "average_rating": round(average_rating, 2),
        "ratings_count": ratings_count,
    }


# PATCH


@router.patch("/movies/{movie_id}/rating", response_model=DisplayRating)
def update_rating_endpoint(
    movie_id: int,
    rating_data: UpdateRating,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return update_rating(movie_id, current_user.id, rating_data, db)


# DELETE


@router.delete("/movies/{movie_id}/rating", status_code=204)
def delete_rating_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    delete_rating(movie_id, current_user.id, db)
