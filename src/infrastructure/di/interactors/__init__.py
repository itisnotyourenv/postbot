from .admin import AdminInteractorProvider
from .auth import AuthInteractorProvider
from .post import PostInteractorProvider
from .referral import ReferralInteractorProvider
from .user import UserInteractorProvider

interactor_providers = [
    AdminInteractorProvider,
    AuthInteractorProvider,
    PostInteractorProvider,
    ReferralInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AdminInteractorProvider",
    "AuthInteractorProvider",
    "PostInteractorProvider",
    "ReferralInteractorProvider",
    "UserInteractorProvider",
    "interactor_providers",
]
