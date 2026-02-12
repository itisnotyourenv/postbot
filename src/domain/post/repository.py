import uuid
from abc import abstractmethod
from typing import Protocol

from src.domain.user.vo import UserId

from .entity import Post


class PostRepository(Protocol):
    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def get_post_by_id(self, post_id: uuid.UUID) -> Post | None:
        raise NotImplementedError

    @abstractmethod
    async def get_post_by_key(self, key: str) -> Post | None:
        raise NotImplementedError

    @abstractmethod
    async def search_posts_by_key(self, unique_key: str, limit: int = 10) -> list[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_posts(
        self, user_id: UserId, offset: int = 0, limit: int = 10
    ) -> list[Post]:
        raise NotImplementedError

    @abstractmethod
    async def count_user_posts(self, user_id: UserId) -> int:
        raise NotImplementedError

    @abstractmethod
    async def soft_delete_post(self, post_id: uuid.UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def key_exists(self, key: str) -> bool:
        raise NotImplementedError
