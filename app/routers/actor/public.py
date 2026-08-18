from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.actor import DisplayActor
from app.schemas.movie import DisplayMovie
from app.services.actor.actor import get_actor, get_actors
from app.services.actor.movie_actor import get_actor_movies

router = APIRouter(prefix="/actors", tags=["Actors"])


# GET


@router.get("", response_model=list[DisplayActor])
def get_actors_endpoint(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_actors(db, offset, page_size)


@router.get("/{actor_id}", response_model=DisplayActor)
def get_actor_endpoint(actor_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_actor(actor_id, db)


@router.get("/{actor_id}/movies", response_model=list[DisplayMovie])
def get_actor_movies_endpoint(
    actor_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_actor_movies(actor_id, db, offset, page_size)
