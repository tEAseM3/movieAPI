from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.language import CreateLanguage, DisplayLanguage, UpdateLanguage
from app.services.language import (
    create_language,
    delete_language,
    update_language,
)

router = APIRouter(prefix="/admin/languages", tags=["Admin Languages"])

# POST


@router.post("", response_model=DisplayLanguage, status_code=201)
def create_language_endpoint(
    language_data: CreateLanguage,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_language(language_data, db)


# PATCH


@router.patch("/{language_id}", response_model=DisplayLanguage)
def update_language_endpoint(
    language_id: int,
    language_data: UpdateLanguage,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return update_language(language_id, language_data, db)


# DELETE


@router.delete("/{language_id}", status_code=204)
def delete_language_endpoint(
    language_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_language(language_id, db)
