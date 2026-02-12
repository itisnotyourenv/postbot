import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.post.entity import Post


@dataclass
class CreatePostInputDTO:
    owner_user_id: int
    content_type: str
    text_md: str | None = None
    telegram_file_id: str | None = None
    buttons_dsl: str | None = None


@dataclass
class CreatePostOutputDTO:
    unique_key: str
    post_id: uuid.UUID


@dataclass
class PostButtonDTO:
    text: str
    url: str
    style: str

    @property
    def pretty_style(self) -> str | None:
        if self.style == "default":
            return None
        elif self.style == "green":
            return "success"
        elif self.style == "blue":
            return "primary"
        elif self.style == "red":
            return "danger"


@dataclass
class PostListItemDTO:
    id: uuid.UUID
    unique_key: str
    content_type: str
    text_preview: str | None
    created_at: datetime


@dataclass
class PostDetailDTO:
    id: uuid.UUID
    unique_key: str
    content_type: str
    text_md: str | None
    telegram_file_id: str | None
    buttons: list[list[PostButtonDTO]]
    created_at: datetime


@dataclass
class PostListOutputDTO:
    items: list[PostListItemDTO]
    total: int
    page: int


def post_to_list_item(post: Post) -> PostListItemDTO:
    text_preview = None
    if post.text_md:
        text_preview = post.text_md.value[:50]
    return PostListItemDTO(
        id=post.id,
        unique_key=post.unique_key.value,
        content_type=post.content_type.value,
        text_preview=text_preview,
        created_at=post.created_at,
    )


def post_to_detail(post: Post) -> PostDetailDTO:
    button_rows: list[list[PostButtonDTO]] = [
        [PostButtonDTO(text=b.text, url=b.url, style=b.style.value) for b in row]
        for row in post.buttons
    ]

    return PostDetailDTO(
        id=post.id,
        unique_key=post.unique_key.value,
        content_type=post.content_type.value,
        text_md=post.text_md.value if post.text_md else None,
        telegram_file_id=post.telegram_file_id.value if post.telegram_file_id else None,
        buttons=button_rows,
        created_at=post.created_at,
    )
