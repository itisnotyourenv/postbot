import uuid
from datetime import UTC, datetime

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.post.entity import Post, PostButton
from src.domain.post.repository import PostRepository
from src.domain.post.vo import (
    ContentType,
    PostStatus,
    TelegramFileId,
    TextMd,
    UniqueKey,
)
from src.domain.user.vo import UserId

from .button_dsl import parse_buttons_dsl
from .dtos import CreatePostInputDTO, CreatePostOutputDTO
from .keygen import generate_unique_key


class CreatePostInteractor(Interactor[CreatePostInputDTO, CreatePostOutputDTO]):
    def __init__(
        self,
        post_repository: PostRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self.post_repository = post_repository
        self.transaction_manager = transaction_manager

    async def __call__(self, data: CreatePostInputDTO) -> CreatePostOutputDTO:
        content_type = ContentType(data.content_type)

        # Validate content
        text_md = None
        if data.text_md:
            text_md = TextMd(data.text_md)

        telegram_file_id = None
        if data.telegram_file_id:
            telegram_file_id = TelegramFileId(data.telegram_file_id)

        if content_type == ContentType.TEXT and not text_md:
            msg = "Text content is required for text posts"
            raise ValueError(msg)

        if (
            content_type in (ContentType.PHOTO, ContentType.VIDEO, ContentType.GIF)
            and not telegram_file_id
        ):
            msg = f"File is required for {content_type.value} posts"
            raise ValueError(msg)

        # Parse buttons DSL
        buttons: list[list[PostButton]] = []
        if data.buttons_dsl:
            parsed_rows = parse_buttons_dsl(data.buttons_dsl)
            buttons = [
                [PostButton(text=btn.text, url=btn.url, style=btn.style) for btn in row]
                for row in parsed_rows
            ]

        # Generate unique key with retry
        unique_key = await self._generate_unique_key()

        now = datetime.now(UTC)
        post = Post(
            id=uuid.uuid4(),
            owner_user_id=UserId(data.owner_user_id),
            unique_key=UniqueKey(unique_key),
            content_type=content_type,
            status=PostStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            text_md=text_md,
            telegram_file_id=telegram_file_id,
            buttons=buttons,
        )

        created_post = await self.post_repository.create_post(post)
        await self.transaction_manager.commit()

        return CreatePostOutputDTO(
            unique_key=created_post.unique_key.value,
            post_id=created_post.id,
        )

    async def _generate_unique_key(self, max_attempts: int = 10) -> str:
        for _ in range(max_attempts):
            key = generate_unique_key()
            if not await self.post_repository.key_exists(key):
                return key
        msg = "Failed to generate unique key after multiple attempts"
        raise RuntimeError(msg)
