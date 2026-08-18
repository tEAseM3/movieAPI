from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.movie import Movie


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(55), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship("Movie", back_populates="language")

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="check_language_name_length"),
        CheckConstraint("length(trim(code)) = 2", name="check_language_code_length"),
    )
