from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.genre import CreateGenre, DisplayGenre, UpdateGenre
from app.services.genre.genre import create_genre, delete_genre, update_genre

router = APIRouter(prefix="/admin/genres", tags=["Admin Genres"])

# POST


@router.post("", response_model=DisplayGenre, status_code=201)
def create_genre_admin_endpoint(
    genre_data: CreateGenre,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_genre(genre_data, db)


# PATCH


@router.patch("/{genre_id}", response_model=DisplayGenre)
def update_genre_admin_endpoint(
    genre_id: int,
    genre_data: UpdateGenre,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return update_genre(genre_id, genre_data, db)


# DELETE


@router.delete("/{genre_id}", status_code=204)
def delete_genre_endpoint(
    genre_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_genre(genre_id, db)
