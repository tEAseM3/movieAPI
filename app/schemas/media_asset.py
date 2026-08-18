import enum
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AssetType(enum.StrEnum):
    poster = "poster"
    backdrop = "backdrop"
    trailer = "trailer"
    still = "still"


class CreateMediaAsset(BaseModel):
    asset_type: AssetType
    filepath: str | None = Field(default=None, max_length=1000)
    url: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def check_filepath_or_url(self):
        if self.filepath is None and self.url is None:
            raise ValueError("Either filepath or url must be provided")
        return self


class UpdateMediaAsset(BaseModel):
    asset_type: AssetType | None = None
    filepath: str | None = Field(default=None, max_length=1000)
    url: str | None = Field(default=None, max_length=1000)


class DisplayMediaAsset(BaseModel):
    id: int
    movie_id: int
    asset_type: AssetType
    filepath: str | None
    url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminDisplayMediaAsset(BaseModel):
    id: int
    movie_id: int
    asset_type: AssetType
    filepath: str | None
    url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}
