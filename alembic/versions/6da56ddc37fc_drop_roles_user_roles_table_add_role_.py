"""drop roles, user_roles table , add role column to users

Revision ID: 6da56ddc37fc
Revises: 7dbefd143a3c
Create Date: 2026-08-13 22:17:10.406994

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6da56ddc37fc"
down_revision: str | Sequence[str] | None = "7dbefd143a3c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
    )

    op.drop_table("user_role")

    op.drop_table("roles")

    op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.String(length=55), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "user_role",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.drop_column("users", "role")
