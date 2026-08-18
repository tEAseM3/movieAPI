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
    from app.models.movie_actor import MovieActor

from app.db.base import Base


class Actor(Base):
    __tablename__ = "actors"

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

    movie_actors: Mapped[list["MovieActor"]] = relationship(back_populates="actor")

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="check_actor_name_length"),
        CheckConstraint("length(trim(surname)) > 0", name="check_actor_surname_length"),
        CheckConstraint("birthdate >= '1800-01-01'", name="check_actor_birthdate"),
        CheckConstraint("length(trim(bio)) <= 2000", name="check_actor_bio_length"),
    )
