from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateActor(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    birthdate: date | None = None
    bio: str | None = Field(default=None, max_length=2000)


class CreateMovieActor(BaseModel):
    character_name: str = Field(min_length=1, max_length=255)


class UpdateActor(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    surname: str | None = Field(default=None, min_length=1, max_length=100)
    birthdate: date | None = None
    bio: str | None = Field(default=None, max_length=2000)


class UpdateMovieActor(BaseModel):
    character_name: str | None = Field(default=None, min_length=1, max_length=255)


class DisplayActor(BaseModel):
    id: int
    name: str
    surname: str
    birthdate: date | None
    bio: str | None

    model_config = {"from_attributes": True}


class AdminDisplayActor(BaseModel):
    id: int
    name: str
    surname: str
    birthdate: date | None
    bio: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class MovieCastMember(BaseModel):
    id: int
    name: str
    surname: str
    character_name: str

    model_config = {"from_attributes": True}
