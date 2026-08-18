from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.movie import AdminDisplayMovie, CreateMovie, UpdateMovie
from app.services.movie import (
    create_movie,
    get_movie_admin,
    get_movies_admin,
    restore_movie,
    soft_delete_movie,
    update_movie,
)

router = APIRouter(prefix="/admin/movies", tags=["Admin Movies"])

# POST


@router.post("", response_model=AdminDisplayMovie, status_code=201)
def create_movie_endpoint(
    movie: CreateMovie,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_movie(movie, db)


# GET


@router.get("/{movie_id}", response_model=AdminDisplayMovie)
def get_movie_admin_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return get_movie_admin(movie_id, db)


@router.get("", response_model=list[AdminDisplayMovie])
def get_movies_admin_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movies_admin(db, offset, page_size)


# PATCH


@router.patch("/{movie_id}", response_model=AdminDisplayMovie)
def update_movie_endpoint(
    movie_id: int,
    movie_data: UpdateMovie,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    movie = update_movie(movie_id, movie_data, db)

    return movie


@router.patch("/{movie_id}/restore", response_model=AdminDisplayMovie)
def restore_movie_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return restore_movie(movie_id, db)


# DELETE


@router.delete("/{movie_id}", response_model=AdminDisplayMovie)
def soft_delete_movie_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    movie = soft_delete_movie(movie_id, db)

    return movie
