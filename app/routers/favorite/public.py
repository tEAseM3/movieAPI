from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.favorite import CreateFavorite, DisplayFavorite
from app.services.favorite import (
    create_favorite,
    delete_favorite,
    get_favorites_by_user,
)

router = APIRouter(tags=["Favorites"])

# POST


@router.post("/movies/{movie_id}/favorite", response_model=DisplayFavorite, status_code=201)
def create_favorite_endpoint(
    movie_id: int,
    favorite_data: CreateFavorite,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return create_favorite(movie_id, current_user.id, favorite_data, db)


# GET


@router.get("/users/me/favorites", response_model=list[DisplayFavorite])
def get_my_favorites_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_favorites_by_user(current_user.id, db, offset, page_size)


# DELETE


@router.delete("/movies/{movie_id}/favorite", status_code=204)
def delete_favorite_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    delete_favorite(movie_id, current_user.id, db)
