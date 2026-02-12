from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Animation, Message, PhotoSize, User, Video
from fluentogram import TranslatorHub

from src.domain.post.vo import ContentType
from src.infrastructure.i18n import create_translator_hub
from src.presentation.bot.routers.post_wizard import (
    _show_preview,
    collect_content,
)


class TestCollectContent:
    """Tests for collect_content handler — verifies html_text is used."""

    @pytest.fixture
    def hub(self) -> TranslatorHub:
        locales_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent / "locales"
        )
        return create_translator_hub(locales_dir)

    @pytest.fixture
    def i18n(self, hub: TranslatorHub):
        return hub.get_translator_by_locale("en")

    @pytest.fixture
    def mock_state(self) -> AsyncMock:
        state = AsyncMock(spec=FSMContext)
        return state

    def _make_message(
        self,
        *,
        text: str | None = None,
        html_text: str | None = None,
        photo: list | None = None,
        video: object | None = None,
        animation: object | None = None,
        caption: str | None = None,
    ) -> MagicMock:
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 123456
        message.text = text
        message.html_text = html_text
        message.caption = caption
        message.photo = photo
        message.video = video
        message.animation = animation
        message.answer = AsyncMock()
        return message

    # --- TEXT content type: html_text should be stored ---

    async def test_text_stores_html_text(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.TEXT.value}
        msg = self._make_message(
            text="Hello **bold**",
            html_text="Hello <b>bold</b>",
        )

        await collect_content(msg, mock_state, i18n)

        mock_state.update_data.assert_called_once_with(
            text_md="Hello <b>bold</b>",
            telegram_file_id=None,
        )

    async def test_text_does_not_store_plain_text(self, mock_state, i18n) -> None:
        """Regression: ensure plain message.text is NOT used as text_md."""
        mock_state.get_data.return_value = {"content_type": ContentType.TEXT.value}
        msg = self._make_message(
            text="plain",
            html_text="<b>formatted</b>",
        )

        await collect_content(msg, mock_state, i18n)

        stored_text_md = mock_state.update_data.call_args.kwargs["text_md"]
        assert stored_text_md != "plain"
        assert stored_text_md == "<b>formatted</b>"

    # --- PHOTO content type: html_text should be stored ---

    async def test_photo_stores_html_text(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.PHOTO.value}
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "photo_file_id_123"
        msg = self._make_message(
            photo=[photo],
            caption="plain caption",
            html_text="<i>italic caption</i>",
        )

        await collect_content(msg, mock_state, i18n)

        mock_state.update_data.assert_called_once_with(
            text_md="<i>italic caption</i>",
            telegram_file_id="photo_file_id_123",
        )

    async def test_photo_does_not_store_plain_caption(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.PHOTO.value}
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "pid"
        msg = self._make_message(
            photo=[photo],
            caption="plain",
            html_text="<b>rich</b>",
        )

        await collect_content(msg, mock_state, i18n)

        stored = mock_state.update_data.call_args.kwargs["text_md"]
        assert stored != "plain"
        assert stored == "<b>rich</b>"

    # --- VIDEO content type: html_text should be stored ---

    async def test_video_stores_html_text(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.VIDEO.value}
        video = MagicMock(spec=Video)
        video.file_id = "video_file_id_456"
        msg = self._make_message(
            video=video,
            caption="plain caption",
            html_text="<b>bold caption</b>",
        )

        await collect_content(msg, mock_state, i18n)

        mock_state.update_data.assert_called_once_with(
            text_md="<b>bold caption</b>",
            telegram_file_id="video_file_id_456",
        )

    # --- GIF content type: html_text should be stored ---

    async def test_gif_stores_html_text(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.GIF.value}
        anim = MagicMock(spec=Animation)
        anim.file_id = "gif_file_id_789"
        msg = self._make_message(
            animation=anim,
            caption="plain",
            html_text="<code>mono</code>",
        )

        await collect_content(msg, mock_state, i18n)

        mock_state.update_data.assert_called_once_with(
            text_md="<code>mono</code>",
            telegram_file_id="gif_file_id_789",
        )

    # --- Wrong content type ---

    async def test_text_type_rejects_photo_message(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.TEXT.value}
        msg = self._make_message(text=None, html_text=None)

        await collect_content(msg, mock_state, i18n)

        msg.answer.assert_called_once()
        mock_state.update_data.assert_not_called()

    # --- Text too long ---

    async def test_text_too_long_rejected(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {"content_type": ContentType.TEXT.value}
        long_text = "x" * 1025
        msg = self._make_message(text=long_text, html_text=long_text)

        await collect_content(msg, mock_state, i18n)

        msg.answer.assert_called_once()
        mock_state.update_data.assert_not_called()


class TestShowPreview:
    """Tests for _show_preview — verifies message.answer() is used for text posts."""

    @pytest.fixture
    def hub(self) -> TranslatorHub:
        locales_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent / "locales"
        )
        return create_translator_hub(locales_dir)

    @pytest.fixture
    def i18n(self, hub: TranslatorHub):
        return hub.get_translator_by_locale("en")

    @pytest.fixture
    def mock_state(self) -> AsyncMock:
        return AsyncMock(spec=FSMContext)

    def _make_message(self) -> MagicMock:
        message = MagicMock(spec=Message)
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()
        message.answer_video = AsyncMock()
        message.answer_animation = AsyncMock()
        # Ensure answer_text does NOT exist, so calling it would raise
        if hasattr(message, "answer_text"):
            del message.answer_text
        # Set up reply on the returned message
        reply_msg = MagicMock()
        reply_msg.reply = AsyncMock()
        message.answer.return_value = reply_msg
        message.answer_photo.return_value = reply_msg
        message.answer_video.return_value = reply_msg
        message.answer_animation.return_value = reply_msg
        return message

    async def test_text_preview_uses_answer(self, mock_state, i18n) -> None:
        """Regression: _show_preview must call message.answer(), not answer_text()."""
        mock_state.get_data.return_value = {
            "content_type": ContentType.TEXT.value,
            "text_md": "<b>Hello</b>",
            "telegram_file_id": None,
            "buttons_dsl": None,
        }
        msg = self._make_message()

        await _show_preview(msg, mock_state, i18n)

        msg.answer.assert_called_once()
        call_kwargs = msg.answer.call_args.kwargs
        assert call_kwargs["text"] == "<b>Hello</b>"

    async def test_photo_preview_uses_answer_photo(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {
            "content_type": ContentType.PHOTO.value,
            "text_md": "caption",
            "telegram_file_id": "photo_123",
            "buttons_dsl": None,
        }
        msg = self._make_message()

        await _show_preview(msg, mock_state, i18n)

        msg.answer_photo.assert_called_once()
        assert msg.answer_photo.call_args.kwargs["photo"] == "photo_123"

    async def test_video_preview_uses_answer_video(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {
            "content_type": ContentType.VIDEO.value,
            "text_md": "caption",
            "telegram_file_id": "video_456",
            "buttons_dsl": None,
        }
        msg = self._make_message()

        await _show_preview(msg, mock_state, i18n)

        msg.answer_video.assert_called_once()
        assert msg.answer_video.call_args.kwargs["video"] == "video_456"

    async def test_gif_preview_uses_answer_animation(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {
            "content_type": ContentType.GIF.value,
            "text_md": "caption",
            "telegram_file_id": "gif_789",
            "buttons_dsl": None,
        }
        msg = self._make_message()

        await _show_preview(msg, mock_state, i18n)

        msg.answer_animation.assert_called_once()
        assert msg.answer_animation.call_args.kwargs["animation"] == "gif_789"

    async def test_text_preview_without_text(self, mock_state, i18n) -> None:
        mock_state.get_data.return_value = {
            "content_type": ContentType.TEXT.value,
            "text_md": None,
            "telegram_file_id": None,
            "buttons_dsl": None,
        }
        msg = self._make_message()

        await _show_preview(msg, mock_state, i18n)

        msg.answer.assert_called_once()
        assert msg.answer.call_args.kwargs["text"] == ""
