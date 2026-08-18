from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.favorite import Favorite
    from app.models.language import Language
    from app.models.media_asset import MediaAsset
    from app.models.movie_actor import MovieActor
    from app.models.movie_director import MovieDirector
    from app.models.movie_genre import MovieGenre
    from app.models.rating import Rating
    from app.models.review import Review

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    duration_time: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    language: Mapped["Language"] = relationship(back_populates="movies")
    movie_actors: Mapped[list["MovieActor"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    movie_directors: Mapped[list["MovieDirector"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    movie_genres: Mapped[list["MovieGenre"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("release_date >= '1895-01-01'::date", name="check_movie_release_date"),
        CheckConstraint("duration_time > 0", name="check_movie_duration_time"),
        CheckConstraint("length(trim(title)) > 0", name="check_movie_title_length"),
        CheckConstraint("length(trim(description)) <= 2000", name="check_movie_description_length"),
        UniqueConstraint("title", "release_date", name="unique_movie_title_release_date"),
    )
