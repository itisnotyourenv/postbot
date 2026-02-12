from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.domain.post.repository import PostRepository
from src.domain.user.vo import UserId

from .dtos import PostListOutputDTO, post_to_list_item

POSTS_PER_PAGE = 10


@dataclass
class GetUserPostsInputDTO:
    user_id: int
    page: int = 1


class GetUserPostsInteractor(Interactor[GetUserPostsInputDTO, PostListOutputDTO]):
    def __init__(self, post_repository: PostRepository) -> None:
        self.post_repository = post_repository

    async def __call__(self, data: GetUserPostsInputDTO) -> PostListOutputDTO:
        user_id = UserId(data.user_id)
        offset = (data.page - 1) * POSTS_PER_PAGE

        posts = await self.post_repository.get_user_posts(
            user_id=user_id, offset=offset, limit=POSTS_PER_PAGE
        )
        total = await self.post_repository.count_user_posts(user_id)

        return PostListOutputDTO(
            items=[post_to_list_item(p) for p in posts],
            total=total,
            page=data.page,
        )
