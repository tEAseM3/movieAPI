from pydantic import BaseModel, Field


class CreateGenre(BaseModel):
    name: str = Field(min_length=1, max_length=55)


class UpdateGenre(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=55)


class DisplayGenre(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
