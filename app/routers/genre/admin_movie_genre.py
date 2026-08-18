from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.services.genre.movie_genre import create_movie_genre, delete_movie_genre

router = APIRouter(prefix="/admin/movies", tags=["Admin Movies"])


# POST


@router.post("/{movie_id}/genres/{genre_id}", status_code=201)
def create_movie_genre_endpoint(
    movie_id: int,
    genre_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    create_movie_genre(movie_id, genre_id, db)


# DELETE


@router.delete("/{movie_id}/genres/{genre_id}", status_code=204)
def delete_movie_genre_endpoint(
    movie_id: int,
    genre_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_movie_genre(movie_id, genre_id, db)
