from pydantic import BaseModel, Field


class CreateRating(BaseModel):
    rating: int = Field(ge=1, le=10)


class UpdateRating(BaseModel):
    rating: int = Field(ge=1, le=10)


class MovieRating(BaseModel):
    average_rating: float
    ratings_count: int


class DisplayRating(BaseModel):
    id: int
    rating: int

    model_config = {"from_attributes": True}
