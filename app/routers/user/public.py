from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UpdateUser, UserCreate, UserDisplay, UserProfile
from app.services.user import create_user, soft_delete_user, update_user

router = APIRouter(prefix="/users", tags=["Users"])

# POST


@router.post("/register", response_model=UserDisplay, status_code=201)
def register_endpoint(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_user(db, user_data)


# GET


@router.get("/me", response_model=UserDisplay)
def get_me_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/me/profile", response_model=UserProfile)
def get_my_profile_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


# PATCH


@router.patch("/me", response_model=UserDisplay)
def update_me_endpoint(
    user_data: UpdateUser,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return update_user(current_user.id, user_data, db)


# DELETE


@router.delete("/me", status_code=204)
def soft_delete_me_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    soft_delete_user(current_user.id, db)
