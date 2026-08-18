from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.genre import DisplayGenre
from app.schemas.movie import DisplayMovie
from app.services.genre.genre import get_genre, get_genre_movies, get_genres

router = APIRouter(prefix="/genres", tags=["Genres"])

# GET


@router.get("", response_model=list[DisplayGenre])
def get_genres_endpoint(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_genres(db, offset, page_size)


@router.get("/{genre_id}", response_model=DisplayGenre)
def get_genre_endpoint(genre_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_genre(genre_id, db)


@router.get("/{genre_id}/movies", response_model=list[DisplayMovie])
def get_genre_movies_endpoint(
    genre_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_genre_movies(genre_id, db, offset, page_size)
