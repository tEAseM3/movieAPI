from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.director import Director
    from app.models.movie import Movie


class MovieDirector(Base):
    __tablename__ = "movie_director"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id", ondelete="CASCADE"), primary_key=True
    )

    movie: Mapped["Movie"] = relationship(back_populates="movie_directors")
    director: Mapped["Director"] = relationship(back_populates="movie_directors")
