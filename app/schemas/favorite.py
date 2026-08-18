from datetime import datetime

from pydantic import BaseModel, Field


class CreateFavorite(BaseModel):
    content: str | None = Field(default=None, max_length=1000)


class DisplayFavorite(BaseModel):
    id: int
    movie_id: int
    content: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
