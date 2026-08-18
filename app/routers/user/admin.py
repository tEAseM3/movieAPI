from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import AdminDisplayUser, UpdateUserRole
from app.services.user import (
    get_user_admin,
    get_users_admin,
    restore_user,
    soft_delete_user,
    update_user_role,
)

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

# GET


@router.get("", response_model=list[AdminDisplayUser])
def get_users_admin_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_users_admin(db, offset, page_size)


@router.get("/{user_id}", response_model=AdminDisplayUser)
def get_user_admin_endpoint(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return get_user_admin(user_id, db)


# PATCH


@router.patch("/{user_id}/role", response_model=AdminDisplayUser)
def update_user_role_endpoint(
    user_id: int,
    role_data: UpdateUserRole,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return update_user_role(user_id, role_data, current_admin, db)


@router.patch("/{user_id}/restore", response_model=AdminDisplayUser)
def restore_user_endpoint(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return restore_user(user_id, db)


# DELETE


@router.delete("/{user_id}", status_code=204)
def soft_delete_user_admin_endpoint(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    soft_delete_user(user_id, db)
