from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.actor import CreateMovieActor, UpdateMovieActor
from app.services.actor.movie_actor import (
    create_movie_actor,
    delete_movie_actor,
    update_movie_actor,
)

router = APIRouter(prefix="/admin/movies", tags=["Admin Movies"])

# POST


@router.post("/{movie_id}/actors/{actor_id}", status_code=201)
def create_movie_actor_endpoint(
    movie_id: int,
    actor_id: int,
    movie_actor_data: CreateMovieActor,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_movie_actor(movie_id, actor_id, movie_actor_data, db)


# PATCH


@router.patch("/{movie_id}/actors/{actor_id}")
def update_movie_actor_endpoint(
    movie_id: int,
    actor_id: int,
    movie_actor_data: UpdateMovieActor,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return update_movie_actor(movie_id, actor_id, movie_actor_data, db)


# DELETE


@router.delete("/{movie_id}/actors/{actor_id}", status_code=204)
def delete_movie_actor_endpoint(
    movie_id: int,
    actor_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_movie_actor(movie_id, actor_id, db)
