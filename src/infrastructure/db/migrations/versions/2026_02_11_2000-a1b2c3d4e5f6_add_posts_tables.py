"""add_posts_tables

Revision ID: a1b2c3d4e5f6
Revises: e0b5590257d6
Create Date: 2026-02-11 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "e0b5590257d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create posts table."""
    op.create_table(
        "posts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("unique_key", sa.String(8), unique=True, nullable=False),
        sa.Column("content_type", sa.String(10), nullable=False),
        sa.Column("text_md", sa.Text(), nullable=True),
        sa.Column("telegram_file_id", sa.Text(), nullable=True),
        sa.Column("buttons", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_index("ix_posts_unique_key", "posts", ["unique_key"], unique=True)
    op.create_index(
        "ix_posts_owner_status_created",
        "posts",
        ["owner_user_id", "status", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    """Drop posts table."""
    op.drop_index("ix_posts_owner_status_created", table_name="posts")
    op.drop_index("ix_posts_unique_key", table_name="posts")
    op.drop_table("posts")
