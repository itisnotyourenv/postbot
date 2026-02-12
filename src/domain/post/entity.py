import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.user.vo import UserId

from .vo import ButtonStyle, ContentType, PostStatus, TelegramFileId, TextMd, UniqueKey


@dataclass
class PostButton:
    text: str
    url: str
    style: ButtonStyle = ButtonStyle.DEFAULT


@dataclass
class Post:
    id: uuid.UUID
    owner_user_id: UserId
    unique_key: UniqueKey
    content_type: ContentType
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    text_md: TextMd | None = None
    telegram_file_id: TelegramFileId | None = None
    buttons: list[list[PostButton]] = field(default_factory=list)
    deleted_at: datetime | None = None
