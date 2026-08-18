from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.media_asset import MediaAssetNotFoundError
from app.models.media_asset import MediaAsset
from app.schemas.media_asset import CreateMediaAsset, UpdateMediaAsset
from app.services.movie import get_movie

# CREATE


def create_media_asset(movie_id: int, asset_data: CreateMediaAsset, db: Session) -> MediaAsset:
    get_movie(movie_id, db)

    media_asset = MediaAsset(
        movie_id=movie_id,
        asset_type=asset_data.asset_type,
        filepath=asset_data.filepath,
        url=asset_data.url,
    )

    db.add(media_asset)
    db.commit()
    db.refresh(media_asset)

    return media_asset


# READ


def get_media_asset(media_asset_id: int, db: Session) -> MediaAsset:
    result = db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_asset_id,
            MediaAsset.deleted_at.is_(None),
        )
    )

    media_asset = result.scalar_one_or_none()
    if media_asset is None:
        raise MediaAssetNotFoundError(f"Media asset with id = {media_asset_id} not found")

    return media_asset


def get_media_asset_admin(media_asset_id: int, db: Session) -> MediaAsset:
    result = db.execute(select(MediaAsset).where(MediaAsset.id == media_asset_id))

    media_asset = result.scalar_one_or_none()
    if media_asset is None:
        raise MediaAssetNotFoundError(f"Media asset with id = {media_asset_id} not found")

    return media_asset


def get_movie_media_assets(
    movie_id: int, db: Session, offset: int = 0, limit: int = 20
) -> list[MediaAsset]:
    get_movie(movie_id, db)

    result = db.execute(
        select(MediaAsset)
        .where(
            MediaAsset.movie_id == movie_id,
            MediaAsset.deleted_at.is_(None),
        )
        .order_by(MediaAsset.id)
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


# UPDATE


def update_media_asset(
    media_asset_id: int, asset_data: UpdateMediaAsset, db: Session
) -> MediaAsset:
    media_asset = get_media_asset(media_asset_id, db)

    update_data = asset_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(media_asset, field, value)

    db.commit()
    db.refresh(media_asset)

    return media_asset


def restore_media_asset(media_asset_id: int, db: Session) -> MediaAsset:
    media_asset = get_media_asset_admin(media_asset_id, db)

    media_asset.deleted_at = None

    db.commit()
    db.refresh(media_asset)

    return media_asset


# DELETE


def soft_delete_media_asset(media_asset_id: int, db: Session) -> MediaAsset:
    media_asset = get_media_asset(media_asset_id, db)

    media_asset.deleted_at = datetime.now(UTC)

    db.commit()
    db.refresh(media_asset)

    return media_asset
