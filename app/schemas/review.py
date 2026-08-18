from datetime import datetime

from pydantic import BaseModel, Field


class CreateReview(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class UpdateReview(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class ReviewAuthor(BaseModel):
    username: str

    model_config = {"from_attributes": True}


class DisplayReview(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: ReviewAuthor

    model_config = {"from_attributes": True}
