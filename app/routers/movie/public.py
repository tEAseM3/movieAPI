from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.actor import MovieCastMember
from app.schemas.director import DisplayDirector
from app.schemas.genre import DisplayGenre
from app.schemas.media_asset import DisplayMediaAsset
from app.schemas.movie import DisplayMovie
from app.services.actor.movie_actor import get_movie_actors
from app.services.director.movie_director import get_movie_directors
from app.services.genre.movie_genre import get_movie_genres
from app.services.media_asset import get_movie_media_assets
from app.services.movie import get_movie, get_movie_by_title, get_movies

router = APIRouter(prefix="/movies", tags=["Movies"])

# GET


@router.get("/search", response_model=list[DisplayMovie])
def search_movies_endpoint(
    movie_title: str,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movie_by_title(movie_title, db, offset, page_size)


@router.get("/{movie_id}", response_model=DisplayMovie)
def get_movie_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_movie(movie_id, db)


@router.get("", response_model=list[DisplayMovie])
def get_movies_endpoint(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movies(db, offset, page_size)


@router.get("/{movie_id}/actors", response_model=list[MovieCastMember])
def get_movie_actors_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movie_actors(movie_id, db, offset, page_size)


@router.get("/{movie_id}/directors", response_model=list[DisplayDirector])
def get_movie_directors_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movie_directors(movie_id, db, offset, page_size)


@router.get("/{movie_id}/genres", response_model=list[DisplayGenre])
def get_movie_genres_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movie_genres(movie_id, db, offset, page_size)


@router.get("/{movie_id}/media-assets", response_model=list[DisplayMediaAsset])
def get_movie_media_assets_endpoint(
    movie_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_movie_media_assets(movie_id, db, offset, page_size)
