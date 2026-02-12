import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update

from src.domain.post.entity import Post
from src.domain.post.repository import PostRepository
from src.domain.post.vo import PostStatus
from src.domain.user.vo import UserId
from src.infrastructure.db.mappers.post import PostMapper
from src.infrastructure.db.models.post import PostModel
from src.infrastructure.db.repos.base import BaseSQLAlchemyRepo


class PostRepositoryImpl(PostRepository, BaseSQLAlchemyRepo):
    async def create_post(self, post: Post) -> Post:
        post_model = PostMapper.to_model(post)
        self._session.add(post_model)
        await self._session.flush()

        return PostMapper.to_domain(post_model)

    async def get_post_by_id(self, post_id: uuid.UUID) -> Post | None:
        stmt = select(PostModel).where(PostModel.id == post_id)
        result = await self._session.execute(stmt)
        post_model = result.scalars().first()

        if post_model is None:
            return None

        return PostMapper.to_domain(post_model)

    async def get_post_by_key(self, key: str) -> Post | None:
        stmt = select(PostModel).where(
            PostModel.unique_key == key,
            PostModel.status == PostStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        post_model = result.scalars().first()

        if post_model is None:
            return None

        return PostMapper.to_domain(post_model)

    async def search_posts_by_key(self, unique_key: str, limit: int = 10) -> list[Post]:
        stmt = (
            select(PostModel)
            .where(
                PostModel.unique_key == unique_key,
                PostModel.status == PostStatus.ACTIVE.value,
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [PostMapper.to_domain(pm) for pm in result.scalars().all()]

    async def get_user_posts(
        self, user_id: UserId, offset: int = 0, limit: int = 10
    ) -> list[Post]:
        stmt = (
            select(PostModel)
            .where(
                PostModel.owner_user_id == user_id.value,
                PostModel.status == PostStatus.ACTIVE.value,
            )
            .order_by(PostModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [PostMapper.to_domain(pm) for pm in result.scalars().all()]

    async def count_user_posts(self, user_id: UserId) -> int:
        stmt = (
            select(func.count())
            .select_from(PostModel)
            .where(
                PostModel.owner_user_id == user_id.value,
                PostModel.status == PostStatus.ACTIVE.value,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def soft_delete_post(self, post_id: uuid.UUID) -> None:
        stmt = (
            update(PostModel)
            .where(PostModel.id == post_id)
            .values(
                status=PostStatus.DELETED.value,
                deleted_at=datetime.now(UTC),
            )
        )
        await self._session.execute(stmt)

    async def key_exists(self, key: str) -> bool:
        stmt = select(select(PostModel).where(PostModel.unique_key == key).exists())
        result = await self._session.execute(stmt)
        return result.scalar() or False
