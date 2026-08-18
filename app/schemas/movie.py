from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateMovie(BaseModel):
    language_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    release_date: date = Field(ge=date(1895, 1, 1))
    duration_time: int = Field(gt=0)


class UpdateMovie(BaseModel):
    language_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    release_date: date | None = Field(default=None, ge=date(1895, 1, 1))
    duration_time: int | None = Field(default=None, gt=0)


class DisplayMovie(BaseModel):
    id: int
    language_id: int
    title: str
    description: str | None
    release_date: date
    duration_time: int

    model_config = {"from_attributes": True}


class AdminDisplayMovie(BaseModel):
    id: int
    language_id: int
    title: str
    description: str | None
    release_date: date
    duration_time: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}
