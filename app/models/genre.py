from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.movie_genre import MovieGenre

from app.db.base import Base


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(55), nullable=False, unique=True)

    movie_genres: Mapped[list["MovieGenre"]] = relationship(back_populates="genre")

    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="check_genre_name"),)
