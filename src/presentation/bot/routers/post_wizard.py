import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.application.post.button_dsl import ButtonDslError, parse_buttons_dsl
from src.application.post.create import CreatePostInteractor
from src.application.post.dtos import CreatePostInputDTO
from src.application.user.dtos import CreateUserOutputDTO
from src.domain.post.vo import ButtonStyle, ContentType
from src.infrastructure.config import Config
from src.presentation.bot.states.post_wizard import PostWizard
from src.presentation.bot.utils import edit_or_answer
from src.presentation.bot.utils.cb_data import (
    MainMenuCBData,
    PostTypeCBData,
    WizardCBData,
)
from src.presentation.bot.utils.markups import back_markup
from src.presentation.bot.utils.markups.post import (
    get_main_menu_keyboard,
    get_post_type_keyboard,
    get_preview_keyboard,
    get_skip_buttons_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="post_wizard")


@router.callback_query(F.data == MainMenuCBData.create_post)
async def start_wizard(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s started post wizard", callback.from_user.id)
    await callback.answer()

    # in case user restarted wizard in the middle, we clear previous data
    await state.clear()
    # Set initial state to choosing post type
    await state.set_state(PostWizard.choosing_type)

    await callback.message.edit_text(
        text=i18n.get("choose-post-type"),
        reply_markup=get_post_type_keyboard(i18n),
    )


@router.callback_query(PostTypeCBData.filter(), PostWizard.choosing_type)
async def choose_type(
    callback: CallbackQuery,
    callback_data: PostTypeCBData,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info(
        "User %s chose post type: %s", callback.from_user.id, callback_data.content_type
    )
    content_type = callback_data.content_type
    await state.update_data(content_type=content_type)
    await state.set_state(PostWizard.collecting_content)

    prompt_key = f"send-{content_type}-content"
    await callback.message.edit_text(
        text=i18n.get(prompt_key),
        reply_markup=back_markup(i18n, MainMenuCBData.create_post),
    )
    await callback.answer()


# --- Collect content ---


@router.message(PostWizard.collecting_content)
async def collect_content(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s submitting post content", message.from_user.id)
    data = await state.get_data()
    content_type = data["content_type"]

    text_md = None
    telegram_file_id = None

    if content_type == ContentType.TEXT.value:
        if not message.text:
            await message.answer(
                i18n.get("wrong-content-type", expected_type=i18n.get("btn-text"))
            )
            return
        if len(message.text) > 1024:
            await message.answer(i18n.get("text-too-long"))
            return
        text_md = message.html_text

    elif content_type == ContentType.PHOTO.value:
        if not message.photo:
            await message.answer(
                i18n.get("wrong-content-type", expected_type=i18n.get("btn-photo"))
            )
            return
        telegram_file_id = message.photo[-1].file_id
        text_md = message.html_text

    elif content_type == ContentType.VIDEO.value:
        if not message.video:
            await message.answer(
                i18n.get("wrong-content-type", expected_type=i18n.get("btn-video"))
            )
            return
        telegram_file_id = message.video.file_id
        text_md = message.html_text

    elif content_type == ContentType.GIF.value:
        if not message.animation:
            await message.answer(
                i18n.get("wrong-content-type", expected_type=i18n.get("btn-gif"))
            )
            return
        telegram_file_id = message.animation.file_id
        text_md = message.html_text

    # Validate caption length
    if text_md and len(text_md) > 1024:
        await message.answer(i18n.get("text-too-long"))
        return

    await state.update_data(text_md=text_md, telegram_file_id=telegram_file_id)
    await state.set_state(PostWizard.collecting_buttons)

    await message.answer(
        text=i18n.get("send-buttons-dsl"),
        reply_markup=get_skip_buttons_keyboard(i18n),
    )


# --- Skip buttons ---


@router.callback_query(
    F.data == WizardCBData.skip_buttons, PostWizard.collecting_buttons
)
async def skip_buttons(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s skipped buttons step", callback.from_user.id)
    await state.update_data(buttons_dsl=None)
    await callback.message.delete_reply_markup()

    await _show_preview(callback.message, state, i18n)
    await callback.answer()


# --- Collect buttons DSL ---


@router.message(PostWizard.collecting_buttons)
async def collect_buttons(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s submitting buttons DSL", message.from_user.id)
    if not message.text:
        await message.answer(i18n.get("invalid-dsl"))
        return

    try:
        parse_buttons_dsl(message.text)
    except ButtonDslError as e:
        await message.answer(str(e))
        return

    await state.update_data(buttons_dsl=message.text)
    await _show_preview(message, state, i18n)


# --- Preview helpers ---


_STYLE_MAP = {
    ButtonStyle.DEFAULT: None,
    ButtonStyle.GREEN: "success",
    ButtonStyle.BLUE: "primary",
    ButtonStyle.RED: "danger",
}


def _build_preview_buttons_keyboard(
    buttons_dsl: str | None,
) -> InlineKeyboardMarkup | None:
    if not buttons_dsl:
        return None
    parsed_rows = parse_buttons_dsl(buttons_dsl)
    keyboard = [
        [
            InlineKeyboardButton(
                text=btn.text,
                url=btn.url,
                style=_STYLE_MAP.get(btn.style),
            )
            for btn in row
        ]
        for row in parsed_rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def _show_preview(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    data = await state.get_data()
    content_type = data["content_type"]
    text_md = data.get("text_md")
    telegram_file_id = data.get("telegram_file_id")
    buttons_dsl = data.get("buttons_dsl")

    buttons_kb = _build_preview_buttons_keyboard(buttons_dsl)

    preview_text = i18n.get("preview-title")
    if text_md:
        preview_text += f"\n\n{text_md}"

    # For media, send content with inline buttons, then preview actions separately
    if telegram_file_id and content_type == ContentType.PHOTO.value:
        media_message = await message.answer_photo(
            photo=telegram_file_id,
            caption=text_md or "",
            reply_markup=buttons_kb,
        )
        await media_message.reply(
            text=i18n.get("preview-title"),
            reply_markup=get_preview_keyboard(i18n),
        )
    elif telegram_file_id and content_type == ContentType.VIDEO.value:
        media_message = await message.answer_video(
            video=telegram_file_id,
            caption=text_md or "",
            reply_markup=buttons_kb,
        )
        await media_message.reply(
            text=i18n.get("preview-title"),
            reply_markup=get_preview_keyboard(i18n),
        )
    elif telegram_file_id and content_type == ContentType.GIF.value:
        media_message = await message.answer_animation(
            animation=telegram_file_id,
            caption=text_md or "",
            reply_markup=buttons_kb,
        )
        await media_message.reply(
            text=i18n.get("preview-title"),
            reply_markup=get_preview_keyboard(i18n),
        )
    elif content_type == ContentType.TEXT.value:
        media_message = await message.answer(
            text=text_md or "",
            reply_markup=buttons_kb,
        )
        await media_message.reply(
            text=i18n.get("preview-title"),
            reply_markup=get_preview_keyboard(i18n),
        )


@router.callback_query(F.data == WizardCBData.confirm)
@inject
async def confirm_post(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
    create_post: FromDishka[CreatePostInteractor],
    config: Config,
) -> None:
    logger.info("User %s confirming post creation", callback.from_user.id)
    data = await state.get_data()

    try:
        result = await create_post(
            CreatePostInputDTO(
                owner_user_id=user.id,
                content_type=data["content_type"],
                text_md=data.get("text_md"),
                telegram_file_id=data.get("telegram_file_id"),
                buttons_dsl=data.get("buttons_dsl"),
            )
        )
    except Exception:
        logger.exception("Failed to create post")
        await callback.message.answer(i18n.get("internal-error"))
        await state.clear()
        await callback.answer()
        return

    await state.clear()

    saved_text = (
        f"{i18n.get('post-saved-header')}\n"
        f"<code>@{config.telegram.bot_username} {result.unique_key}</code>"
    )
    await callback.message.answer(
        text=saved_text,
        reply_markup=get_main_menu_keyboard(i18n),
    )
    await callback.answer()


# --- Restart (Edit) ---


@router.callback_query(F.data == WizardCBData.restart)
async def restart_wizard(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s restarted post wizard", callback.from_user.id)
    await state.clear()
    await state.set_state(PostWizard.choosing_type)
    await callback.message.answer(
        text=i18n.get("choose-post-type"),
        reply_markup=get_post_type_keyboard(i18n),
    )
    await callback.answer()


# --- Cancel ---


@router.callback_query(F.data == WizardCBData.cancel)
async def cancel_wizard(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    logger.info("User %s cancelled post wizard", callback.from_user.id)
    await state.clear()
    await callback.answer()
    await edit_or_answer(
        callback,
        text=i18n.get("main-menu"),  # main menu text
        reply_markup=get_main_menu_keyboard(i18n),
    )
