from dishka import Provider, Scope, provide

from src.application.common.transaction import TransactionManager
from src.application.post.create import CreatePostInteractor
from src.application.post.delete import DeletePostInteractor
from src.application.post.get_detail import GetPostDetailInteractor
from src.application.post.get_user_posts import GetUserPostsInteractor
from src.application.post.search_by_key import SearchPostsByKeyInteractor
from src.domain.post.repository import PostRepository


class PostInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_create_post_interactor(
        self,
        post_repository: PostRepository,
        transaction_manager: TransactionManager,
    ) -> CreatePostInteractor:
        return CreatePostInteractor(
            post_repository=post_repository,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_get_user_posts_interactor(
        self,
        post_repository: PostRepository,
    ) -> GetUserPostsInteractor:
        return GetUserPostsInteractor(post_repository=post_repository)

    @provide
    def provide_get_post_detail_interactor(
        self,
        post_repository: PostRepository,
    ) -> GetPostDetailInteractor:
        return GetPostDetailInteractor(post_repository=post_repository)

    @provide
    def provide_delete_post_interactor(
        self,
        post_repository: PostRepository,
        transaction_manager: TransactionManager,
    ) -> DeletePostInteractor:
        return DeletePostInteractor(
            post_repository=post_repository,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_search_posts_by_key_interactor(
        self,
        post_repository: PostRepository,
    ) -> SearchPostsByKeyInteractor:
        return SearchPostsByKeyInteractor(post_repository=post_repository)
