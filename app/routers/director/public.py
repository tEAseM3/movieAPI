from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.director import DisplayDirector
from app.schemas.movie import DisplayMovie
from app.services.director.director import get_director, get_directors
from app.services.director.movie_director import get_director_movies

router = APIRouter(prefix="/directors", tags=["Directors"])

# GET


@router.get("", response_model=list[DisplayDirector])
def get_directors_endpoint(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_directors(db, offset, page_size)


@router.get("/{director_id}", response_model=DisplayDirector)
def get_director_endpoint(director_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_director(director_id, db)


@router.get("/{director_id}/movies", response_model=list[DisplayMovie])
def get_director_movies_endpoint(
    director_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_director_movies(director_id, db, offset, page_size)
