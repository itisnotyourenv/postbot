from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.post.repository import PostRepository

from .dtos import PostDetailDTO, post_to_detail


@dataclass
class SearchPostsByKeyInputDTO:
    query: str


class SearchPostsByKeyInteractor(
    Interactor[SearchPostsByKeyInputDTO, list[PostDetailDTO]]
):
    def __init__(self, post_repository: PostRepository) -> None:
        self.post_repository = post_repository

    async def __call__(self, data: SearchPostsByKeyInputDTO) -> list[PostDetailDTO]:
        query = data.query.strip().lower()
        if not query:
            return []

        posts = await self.post_repository.search_posts_by_key(
            unique_key=query, limit=10
        )
        return [post_to_detail(p) for p in posts]
