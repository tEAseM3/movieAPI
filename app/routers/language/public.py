from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.language import DisplayLanguage
from app.schemas.movie import DisplayMovie
from app.services.language import get_language, get_language_movies, get_languages

router = APIRouter(prefix="/languages", tags=["Languages"])

# GET


@router.get("/{language_id}", response_model=DisplayLanguage)
def get_language_endpoint(
    language_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_language(language_id, db)


@router.get("", response_model=list[DisplayLanguage])
def get_languages_endpoint(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size

    return get_languages(db, offset, page_size)


@router.get("/{language_id}/movies", response_model=list[DisplayMovie])
def get_language_movies_endpoint(
    language_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size

    return get_language_movies(language_id, db, offset, page_size)
