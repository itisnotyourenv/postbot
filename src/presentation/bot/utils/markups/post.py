from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from src.application.post.dtos import PostButtonDTO, PostListItemDTO
from src.domain.post.vo import ContentType
from src.presentation.bot.utils.cb_data import (
    MainMenuCBData,
    MyPostsCBData,
    PostTypeCBData,
    WizardCBData,
)

POSTS_PER_PAGE = 10


def get_main_menu_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Main menu with Create Post and My Posts buttons in one row."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-create-post"),
                    callback_data=MainMenuCBData.create_post,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-my-posts"),
                    callback_data=MainMenuCBData.my_posts,
                ),
            ],
        ]
    )


def get_post_type_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Post type selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-photo"),
                    callback_data=PostTypeCBData(
                        content_type=ContentType.PHOTO.value
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("btn-video"),
                    callback_data=PostTypeCBData(
                        content_type=ContentType.VIDEO.value
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-text"),
                    callback_data=PostTypeCBData(
                        content_type=ContentType.TEXT.value
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("btn-gif"),
                    callback_data=PostTypeCBData(
                        content_type=ContentType.GIF.value
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-cancel"),
                    callback_data=WizardCBData.cancel,
                ),
            ],
        ]
    )


def get_skip_buttons_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Skip buttons step or cancel."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-skip"),
                    callback_data=WizardCBData.skip_buttons,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-cancel"),
                    callback_data=WizardCBData.cancel,
                ),
            ],
        ]
    )


def get_preview_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    """Preview action buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-confirm"),
                    callback_data=WizardCBData.confirm,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-cancel"),
                    callback_data=WizardCBData.cancel,
                ),
            ],
        ]
    )


def get_my_posts_keyboard(
    posts: list[PostListItemDTO],
    page: int,
    total: int,
    i18n: TranslatorRunner,
) -> InlineKeyboardMarkup:
    """Paginated list of user posts."""
    keyboard: list[list[InlineKeyboardButton]] = []

    for post in posts:
        type_label = post.content_type
        date_str = post.created_at.strftime("%d.%m.%Y")
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{post.unique_key} | {type_label} | {date_str}",
                    callback_data=MyPostsCBData(
                        action="preview", post_id=str(post.id)
                    ).pack(),
                ),
            ]
        )

    # Pagination
    total_pages = max(1, (total + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE)
    nav_buttons: list[InlineKeyboardButton] = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=i18n.get("btn-prev-page"),
                callback_data=MyPostsCBData(action="page", page=page - 1).pack(),
            )
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=i18n.get("btn-next-page"),
                callback_data=MyPostsCBData(action="page", page=page + 1).pack(),
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append(
        [
            InlineKeyboardButton(
                text=i18n.get("btn-back-to-menu"),
                callback_data=MainMenuCBData.menu,
            ),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_post_actions_keyboard(
    post_id: str, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Actions for a single post: Preview and Delete."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-delete"),
                    callback_data=MyPostsCBData(
                        action="delete", post_id=post_id
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-back-to-list"),
                    callback_data=MyPostsCBData(action="page", page=1).pack(),
                ),
            ],
        ]
    )


def get_delete_confirm_keyboard(
    post_id: str, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Confirm deletion keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-delete-yes"),
                    callback_data=MyPostsCBData(
                        action="delete_confirm", post_id=post_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("btn-cancel"),
                    callback_data=MyPostsCBData(
                        action="preview", post_id=post_id
                    ).pack(),
                ),
            ],
        ]
    )


def get_post_saved_keyboard(
    unique_key: str, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Post saved message keyboard with Share and main menu buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-share"),
                    switch_inline_query=unique_key,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-create-post"),
                    callback_data=MainMenuCBData.create_post,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-my-posts"),
                    callback_data=MainMenuCBData.my_posts,
                ),
            ],
        ]
    )


def build_inline_keyboard_from_buttons(
    button_rows: list[list[PostButtonDTO]],
) -> InlineKeyboardMarkup | None:
    """Convert post button DTOs to an InlineKeyboardMarkup."""
    if not button_rows:
        return None

    keyboard: list[list[InlineKeyboardButton]] = []
    for row in button_rows:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=btn.text,
                    url=btn.url,
                    style=btn.pretty_style,
                )
                for btn in row
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
