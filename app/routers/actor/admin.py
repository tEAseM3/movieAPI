from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.actor import (
    AdminDisplayActor,
    CreateActor,
    UpdateActor,
)
from app.services.actor.actor import (
    create_actor,
    get_actor_admin,
    get_actors_admin,
    restore_actor,
    soft_delete_actor,
    update_actor,
)

router = APIRouter(prefix="/admin/actors", tags=["Admin Actor"])


# POST


@router.post("", status_code=201)
def create_actor_endpoint(
    actor_data: CreateActor,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_actor(actor_data, db)


# GET


@router.get("", response_model=list[AdminDisplayActor])
def get_actors_admin_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_actors_admin(db, offset, page_size)


@router.get("/{actor_id}", response_model=AdminDisplayActor)
def get_actor_admin_endpoint(
    actor_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return get_actor_admin(actor_id, db)


# PATCH


@router.patch("/{actor_id}", response_model=AdminDisplayActor)
def update_actor_endpoint(
    actor_id: int,
    actor_data: UpdateActor,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return update_actor(actor_id, actor_data, db)


@router.patch("/{actor_id}/restore", response_model=AdminDisplayActor)
def restore_actor_endpoint(
    actor_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return restore_actor(actor_id, db)


# DELETE


@router.delete("/{actor_id}", response_model=AdminDisplayActor)
def soft_delete_actor_endpoint(
    actor_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):

    return soft_delete_actor(actor_id, db)
