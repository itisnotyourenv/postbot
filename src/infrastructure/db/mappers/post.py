from src.domain.post.entity import Post, PostButton
from src.domain.post.vo import (
    ButtonStyle,
    ContentType,
    PostStatus,
    TelegramFileId,
    TextMd,
    UniqueKey,
)
from src.domain.user.vo import UserId
from src.infrastructure.db.models.post import PostModel


class PostMapper:
    @staticmethod
    def to_domain(model: PostModel) -> Post:
        buttons: list[list[PostButton]] = [
            [
                PostButton(
                    text=btn["text"],
                    url=btn["url"],
                    style=ButtonStyle(btn["style"]),
                )
                for btn in row
            ]
            for row in (model.buttons or [])
        ]

        owner_user_id = (
            model.owner_user_id
            if isinstance(model.owner_user_id, UserId)
            else UserId(model.owner_user_id)
        )

        return Post(
            id=model.id,
            owner_user_id=owner_user_id,
            unique_key=UniqueKey(model.unique_key),
            content_type=ContentType(model.content_type),
            status=PostStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            text_md=TextMd(model.text_md) if model.text_md else None,
            telegram_file_id=(
                TelegramFileId(model.telegram_file_id)
                if model.telegram_file_id
                else None
            ),
            buttons=buttons,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(post: Post) -> PostModel:
        buttons_json: list[list[dict]] = [
            [
                {"text": btn.text, "url": btn.url, "style": btn.style.value}
                for btn in row
            ]
            for row in post.buttons
        ]

        return PostModel(
            id=post.id,
            owner_user_id=post.owner_user_id.value,
            unique_key=post.unique_key.value,
            content_type=post.content_type.value,
            text_md=post.text_md.value if post.text_md else None,
            telegram_file_id=(
                post.telegram_file_id.value if post.telegram_file_id else None
            ),
            buttons=buttons_json,
            status=post.status.value,
            created_at=post.created_at,
            updated_at=post.updated_at,
            deleted_at=post.deleted_at,
        )
