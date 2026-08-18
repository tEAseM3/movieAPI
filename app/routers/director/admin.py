from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.director import (
    AdminDisplayDirector,
    CreateDirector,
    UpdateDirector,
)
from app.services.director.director import (
    create_director,
    get_director_admin,
    get_directors_admin,
    restore_director,
    soft_delete_director,
    update_director,
)

router = APIRouter(prefix="/admin/directors", tags=["Admin Director"])

# POST


@router.post("", status_code=201)
def create_director_endpoint(
    director: CreateDirector,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_director(director, db)


# GET


@router.get("", response_model=list[AdminDisplayDirector])
def get_directors_admin_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_directors_admin(db, offset, page_size)


@router.get("/{director_id}", response_model=AdminDisplayDirector)
def get_director_admin_endpoint(
    director_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return get_director_admin(director_id, db)


# PATCH


@router.patch("/{director_id}", response_model=AdminDisplayDirector)
def update_director_endpoint(
    director_id: int,
    director_data: UpdateDirector,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return update_director(director_id, director_data, db)


@router.patch("/{director_id}/restore", response_model=AdminDisplayDirector)
def restore_director_endpoint(
    director_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return restore_director(director_id, db)


# DELETE


@router.delete("/{director_id}", response_model=AdminDisplayDirector)
def soft_delete_director_endpoint(
    director_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return soft_delete_director(director_id, db)
