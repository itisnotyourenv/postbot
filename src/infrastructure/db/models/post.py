import uuid
from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORMModel


class PostModel(BaseORMModel):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    unique_key: Mapped[str] = mapped_column(
        String(8), unique=True, nullable=False, index=True
    )
    content_type: Mapped[str] = mapped_column(String(10), nullable=False)
    text_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    buttons: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            "ix_posts_owner_status_created",
            "owner_user_id",
            "status",
            created_at.desc(),
        ),
    )
