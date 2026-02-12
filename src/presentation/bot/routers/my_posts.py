import logging
import uuid

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.application.post.delete import DeletePostInputDTO, DeletePostInteractor
from src.application.post.get_detail import (
    GetPostDetailInputDTO,
    GetPostDetailInteractor,
)
from src.application.post.get_user_posts import (
    GetUserPostsInputDTO,
    GetUserPostsInteractor,
)
from src.application.user.dtos import CreateUserOutputDTO
from src.infrastructure.config import Config
from src.presentation.bot.utils.cb_data import MainMenuCBData, MyPostsCBData
from src.presentation.bot.utils.markups.post import (
    build_inline_keyboard_from_buttons,
    get_delete_confirm_keyboard,
    get_main_menu_keyboard,
    get_my_posts_keyboard,
    get_post_actions_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="my_posts")


@router.callback_query(F.data == MainMenuCBData.my_posts)
@inject
async def my_posts_list(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
    get_user_posts: FromDishka[GetUserPostsInteractor],
) -> None:
    logger.info("User %s opened my posts list", callback.from_user.id)
    await _show_posts_page(callback, i18n, user, get_user_posts, page=1)


@router.callback_query(MyPostsCBData.filter(F.action == "page"))
@inject
async def my_posts_page(
    callback: CallbackQuery,
    callback_data: MyPostsCBData,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
    get_user_posts: FromDishka[GetUserPostsInteractor],
) -> None:
    logger.info(
        "User %s navigated to posts page %s", callback.from_user.id, callback_data.page
    )
    await _show_posts_page(
        callback, i18n, user, get_user_posts, page=callback_data.page
    )


async def _show_posts_page(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
    get_user_posts: GetUserPostsInteractor,
    page: int,
) -> None:
    result = await get_user_posts(GetUserPostsInputDTO(user_id=user.id, page=page))

    if not result.items:
        await callback.message.edit_text(
            text=i18n.get("my-posts-empty"),
            reply_markup=get_main_menu_keyboard(i18n),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text=i18n.get("my-posts-title", count=str(result.total)),
        reply_markup=get_my_posts_keyboard(
            result.items, result.page, result.total, i18n
        ),
    )
    await callback.answer()


@router.callback_query(MyPostsCBData.filter(F.action == "preview"))
@inject
async def preview_post(
    callback: CallbackQuery,
    callback_data: MyPostsCBData,
    i18n: TranslatorRunner,
    get_post_detail: FromDishka[GetPostDetailInteractor],
    config: FromDishka[Config],
) -> None:
    logger.info(
        "User %s previewing post %s", callback.from_user.id, callback_data.post_id
    )
    post = await get_post_detail(
        GetPostDetailInputDTO(post_id=uuid.UUID(callback_data.post_id))
    )

    if post is None:
        await callback.answer(i18n.get("inline-not-found"))
        return

    inline_kb = build_inline_keyboard_from_buttons(post.buttons)
    actions_kb = get_post_actions_keyboard(callback_data.post_id, post.unique_key, i18n)

    # Send content based on type
    if post.telegram_file_id and post.content_type == "photo":
        content_message = await callback.message.answer_photo(
            photo=post.telegram_file_id,
            caption=post.text_md or "",
            reply_markup=inline_kb,
        )
    elif post.telegram_file_id and post.content_type == "video":
        content_message = await callback.message.answer_video(
            video=post.telegram_file_id,
            caption=post.text_md or "",
            reply_markup=inline_kb,
        )
    elif post.telegram_file_id and post.content_type == "gif":
        content_message = await callback.message.answer_animation(
            animation=post.telegram_file_id,
            caption=post.text_md or "",
            reply_markup=inline_kb,
        )
    else:
        text = post.text_md or ""
        content_message = await callback.message.answer(
            text=text,
            reply_markup=inline_kb,
        )

    # Send actions separately
    hint_text = (
        f"🔑 <code>@{config.telegram.bot_username} {post.unique_key}</code>\n\n"
        f"{i18n.get('post-actions-hint')}"
    )
    await content_message.reply(
        text=hint_text,
        reply_markup=actions_kb,
    )
    await callback.answer()


@router.callback_query(MyPostsCBData.filter(F.action == "delete"))
async def delete_post_confirm(
    callback: CallbackQuery,
    callback_data: MyPostsCBData,
    i18n: TranslatorRunner,
) -> None:
    logger.info(
        "User %s requested delete confirmation for post %s",
        callback.from_user.id,
        callback_data.post_id,
    )
    await callback.message.edit_text(
        text=i18n.get("delete-confirm"),
        reply_markup=get_delete_confirm_keyboard(callback_data.post_id, i18n),
    )
    await callback.answer()


@router.callback_query(MyPostsCBData.filter(F.action == "delete_confirm"))
@inject
async def delete_post_execute(
    callback: CallbackQuery,
    callback_data: MyPostsCBData,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
    delete_post: FromDishka[DeletePostInteractor],
) -> None:
    logger.info(
        "User %s confirmed deletion of post %s",
        callback.from_user.id,
        callback_data.post_id,
    )
    success = await delete_post(
        DeletePostInputDTO(
            post_id=uuid.UUID(callback_data.post_id),
            user_id=user.id,
        )
    )

    if success:
        await callback.message.edit_text(
            text=i18n.get("post-deleted"),
            reply_markup=get_main_menu_keyboard(i18n),
        )
    else:
        await callback.message.edit_text(
            text=i18n.get("internal-error"),
            reply_markup=get_main_menu_keyboard(i18n),
        )
    await callback.answer()
