from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.services.director.movie_director import (
    create_movie_director,
    delete_movie_director,
)

router = APIRouter(prefix="/admin/directors", tags=["Admin Director"])

# POST


@router.post("/{director_id}/movies/{movie_id}", status_code=201)
def create_movie_director_endpoint(
    director_id: int,
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_movie_director(movie_id, director_id, db)


# DELETE


@router.delete("/{director_id}/movies/{movie_id}", status_code=204)
def delete_movie_director_endpoint(
    director_id: int,
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_movie_director(movie_id, director_id, db)
