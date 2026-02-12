from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner


def back_markup(i18n: TranslatorRunner, callback_data: str) -> InlineKeyboardMarkup:
    """A simple back button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("btn-back"),
                    callback_data=callback_data,
                ),
            ],
        ]
    )
