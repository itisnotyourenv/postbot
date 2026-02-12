import hashlib
import logging

from aiogram import Router
from aiogram.types import (
    ChosenInlineResult,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedGif,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVideo,
    InputTextMessageContent,
)
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.application.post.dtos import PostDetailDTO
from src.application.post.search_by_key import (
    SearchPostsByKeyInputDTO,
    SearchPostsByKeyInteractor,
)
from src.presentation.bot.utils.markups.post import build_inline_keyboard_from_buttons

logger = logging.getLogger(__name__)

router = Router(name="inline")


@router.inline_query()
@inject
async def inline_query_handler(
    query: InlineQuery,
    i18n: TranslatorRunner,
    search_posts: FromDishka[SearchPostsByKeyInteractor],
) -> None:
    logger.info("User %s inline query: %r", query.from_user.id, query.query)
    search_text = query.query.strip()

    if not search_text:
        await query.answer(
            results=[],
            cache_time=5,
            is_personal=True,
            switch_pm_text=i18n.get("open-bot-to-create-post"),
            switch_pm_parameter="start",
        )
        return

    posts = await search_posts(SearchPostsByKeyInputDTO(query=search_text))

    if not posts:
        await query.answer(
            results=[],
            cache_time=5,
            is_personal=True,
            switch_pm_text=i18n.get("inline-not-found"),
            switch_pm_parameter="start",
        )
        return

    results = []
    for post in posts:
        result = _build_inline_result(post)
        if result:
            results.append(result)

    await query.answer(
        results=results,
        cache_time=5,
        is_personal=False,
    )


def _build_inline_result(
    post: PostDetailDTO,
) -> (
    InlineQueryResultArticle
    | InlineQueryResultCachedPhoto
    | InlineQueryResultCachedVideo
    | InlineQueryResultCachedGif
    | None
):
    result_id = hashlib.md5(post.unique_key.encode()).hexdigest()  # noqa: S324
    reply_markup = build_inline_keyboard_from_buttons(post.buttons)

    if post.content_type == "text":
        return InlineQueryResultArticle(
            id=result_id,
            title=post.text_md[:50] if post.text_md else post.unique_key,
            description=post.text_md[:100] if post.text_md else "",
            input_message_content=InputTextMessageContent(
                message_text=post.text_md or "",
            ),
            reply_markup=reply_markup,
        )

    if post.content_type == "photo" and post.telegram_file_id:
        return InlineQueryResultCachedPhoto(
            id=result_id,
            photo_file_id=post.telegram_file_id,
            caption=post.text_md or "",
            reply_markup=reply_markup,
        )

    if post.content_type == "video" and post.telegram_file_id:
        return InlineQueryResultCachedVideo(
            id=result_id,
            video_file_id=post.telegram_file_id,
            title=post.text_md[:50] if post.text_md else post.unique_key,
            caption=post.text_md or "",
            reply_markup=reply_markup,
        )

    if post.content_type == "gif" and post.telegram_file_id:
        return InlineQueryResultCachedGif(
            id=result_id,
            gif_file_id=post.telegram_file_id,
            caption=post.text_md or "",
            reply_markup=reply_markup,
        )

    return None


@router.chosen_inline_result()
async def chosen_inline_result_handler(
    chosen_result: ChosenInlineResult,
) -> None:
    logger.info(
        "Inline result chosen: query=%s, result_id=%s, user_id=%s",
        chosen_result.query,
        chosen_result.result_id,
        chosen_result.from_user.id,
    )
