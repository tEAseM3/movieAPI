from pydantic import BaseModel, EmailStr, Field

from app.models.user import RoleEnum


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=55)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UpdateUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=55)
    email: EmailStr | None = None


class UpdateUserRole(BaseModel):
    role: RoleEnum


class UserDisplay(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class ProfileReview(BaseModel):
    id: int
    movie_id: int
    content: str

    model_config = {"from_attributes": True}


class ProfileRating(BaseModel):
    id: int
    movie_id: int
    rating: int

    model_config = {"from_attributes": True}


class ProfileFavorite(BaseModel):
    id: int
    movie_id: int
    content: str | None

    model_config = {"from_attributes": True}


class UserProfile(UserDisplay):
    reviews: list[ProfileReview]
    ratings: list[ProfileRating]
    favorites: list[ProfileFavorite]


class AdminDisplayUser(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum

    model_config = {"from_attributes": True}
