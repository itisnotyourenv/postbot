import uuid
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.post.repository import PostRepository

from .dtos import PostDetailDTO, post_to_detail


@dataclass
class GetPostDetailInputDTO:
    post_id: uuid.UUID


class GetPostDetailInteractor(Interactor[GetPostDetailInputDTO, PostDetailDTO | None]):
    def __init__(self, post_repository: PostRepository) -> None:
        self.post_repository = post_repository

    async def __call__(self, data: GetPostDetailInputDTO) -> PostDetailDTO | None:
        post = await self.post_repository.get_post_by_id(data.post_id)
        if post is None:
            return None
        return post_to_detail(post)
