from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.movie_director import MovieDirector

from app.db.base import Base


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    movie_directors: Mapped[list["MovieDirector"]] = relationship(back_populates="director")

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="check_director_name"),
        CheckConstraint("length(trim(surname)) > 0", name="check_director_surname_length"),
        CheckConstraint("birthdate >= '1800-01-01'", name="check_director_birthdate"),
        CheckConstraint("length(trim(bio)) <= 2000", name="check_director_bio_length"),
    )
