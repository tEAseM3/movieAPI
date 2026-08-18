from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.actor import Actor
    from app.models.movie import Movie


class MovieActor(Base):
    __tablename__ = "movie_actor"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True
    )
    character_name: Mapped[str] = mapped_column(String(255), nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="movie_actors")
    actor: Mapped["Actor"] = relationship(back_populates="movie_actors")

    __table_args__ = (
        CheckConstraint(
            "length(trim(character_name)) > 0", name="check_actor_character_name_length"
        ),
    )
