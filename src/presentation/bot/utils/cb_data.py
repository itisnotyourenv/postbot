from aiogram.filters.callback_data import CallbackData


class SettingsCBData:
    menu: str = "settings:menu"
    language: str = "settings:language"
    back: str = "settings:back"


class LanguageCBData(CallbackData, prefix="lang"):
    code: str  # "en" or "ru"


class OnboardingCBData(CallbackData, prefix="onboard"):
    code: str  # "en" or "ru"


# Post-related callback data


class MainMenuCBData:
    menu: str = "main:menu"
    create_post: str = "main:create_post"
    my_posts: str = "main:my_posts"


class PostTypeCBData(CallbackData, prefix="ptype"):
    content_type: str  # text, photo, video, gif


class WizardCBData:
    skip_buttons: str = "wizard:skip_buttons"
    confirm: str = "wizard:confirm"
    restart: str = "wizard:restart"
    cancel: str = "wizard:cancel"


class MyPostsCBData(CallbackData, prefix="myposts"):
    action: str  # page, preview, delete, delete_confirm, back
    post_id: str = ""  # UUID as string
    page: int = 1
