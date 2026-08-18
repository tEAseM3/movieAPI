from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.media_asset import AdminDisplayMediaAsset, CreateMediaAsset, UpdateMediaAsset
from app.services.media_asset import (
    create_media_asset,
    get_media_asset_admin,
    restore_media_asset,
    soft_delete_media_asset,
    update_media_asset,
)

router = APIRouter(prefix="/admin/media-assets", tags=["Admin Media Assets"])

# POST


@router.post("/{movie_id}", response_model=AdminDisplayMediaAsset, status_code=201)
def create_movie_media_asset_endpoint(
    movie_id: int,
    asset_data: CreateMediaAsset,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return create_media_asset(movie_id, asset_data, db)


# GET


@router.get("/{media_asset_id}", response_model=AdminDisplayMediaAsset)
def get_media_asset_admin_endpoint(
    media_asset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return get_media_asset_admin(media_asset_id, db)


# PATCH


@router.patch("/{media_asset_id}", response_model=AdminDisplayMediaAsset)
def update_media_asset_endpoint(
    media_asset_id: int,
    asset_data: UpdateMediaAsset,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return update_media_asset(media_asset_id, asset_data, db)


@router.patch("/{media_asset_id}/restore", response_model=AdminDisplayMediaAsset)
def restore_media_asset_endpoint(
    media_asset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return restore_media_asset(media_asset_id, db)


# DELETE


@router.delete("/{media_asset_id}", response_model=AdminDisplayMediaAsset)
def soft_delete_media_asset_endpoint(
    media_asset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    return soft_delete_media_asset(media_asset_id, db)
