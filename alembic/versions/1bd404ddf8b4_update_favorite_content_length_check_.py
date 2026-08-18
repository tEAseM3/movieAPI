"""update favorite content length check constraint

Revision ID: 1bd404ddf8b4
Revises: 957b1368e684
Create Date: 2026-08-09 20:26:34.386924

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bd404ddf8b4"
down_revision: str | Sequence[str] | None = "957b1368e684"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "check_favorite_content_length",
        "favorites",
        type_="check",
    )

    op.create_check_constraint(
        "check_favorite_content_length",
        "favorites",
        "length(trim(content)) <= 1000",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_favorite_content_length",
        "favorites",
        type_="check",
    )

    op.create_check_constraint(
        "check_favorite_content_length",
        "favorites",
        "length(trim(content)) > 0",
    )
