from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateDirector(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    birthdate: date | None = None
    bio: str | None = Field(default=None, max_length=2000)


class UpdateDirector(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    surname: str | None = Field(default=None, min_length=1, max_length=100)
    birthdate: date | None = None
    bio: str | None = Field(default=None, max_length=2000)


class DisplayDirector(BaseModel):
    id: int
    name: str
    surname: str
    birthdate: date | None
    bio: str | None

    model_config = {"from_attributes": True}


class AdminDisplayDirector(BaseModel):
    id: int
    name: str
    surname: str
    birthdate: date | None
    bio: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}
