from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Text,
    UniqueConstraint,
    func,
)

if TYPE_CHECKING:
    from app.models.movie import Movie
    from app.models.user import User

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    movie: Mapped["Movie"] = relationship(back_populates="favorites")
    user: Mapped["User"] = relationship(back_populates="favorites")

    __table_args__ = (
        CheckConstraint("length(trim(content)) <= 1000", name="check_favorite_content_length"),
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_favorite"),
    )
