from pydantic import BaseModel, Field


class CreateLanguage(BaseModel):
    name: str = Field(min_length=1, max_length=55)
    code: str = Field(min_length=2, max_length=2)


class UpdateLanguage(BaseModel):
    name: str | None = Field(default=None, max_length=55)
    code: str | None = Field(default=None, min_length=2, max_length=2)


class DisplayLanguage(BaseModel):
    id: int
    name: str
    code: str

    model_config = {"from_attributes": True}
