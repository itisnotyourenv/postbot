import uuid
from dataclasses import dataclass

from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.post.repository import PostRepository


@dataclass
class DeletePostInputDTO:
    post_id: uuid.UUID
    user_id: int


class DeletePostInteractor(Interactor[DeletePostInputDTO, bool]):
    def __init__(
        self,
        post_repository: PostRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self.post_repository = post_repository
        self.transaction_manager = transaction_manager

    async def __call__(self, data: DeletePostInputDTO) -> bool:
        post = await self.post_repository.get_post_by_id(data.post_id)
        if post is None:
            return False

        # Ownership check
        if post.owner_user_id.value != data.user_id:
            return False

        await self.post_repository.soft_delete_post(data.post_id)
        await self.transaction_manager.commit()
        return True
