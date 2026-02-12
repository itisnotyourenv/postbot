import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.application.referral.process import (
    ProcessReferralInputDTO,
    ProcessReferralInteractor,
)
from src.application.user.dtos import CreateUserOutputDTO
from src.presentation.bot.utils.cb_data import MainMenuCBData
from src.presentation.bot.utils.markups.post import get_main_menu_keyboard
from src.presentation.bot.utils.markups.settings import (
    get_onboarding_language_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="commands")


async def _process_referral_if_applicable(
    user_id: int,
    command: CommandObject,
    process_referral: ProcessReferralInteractor,
) -> None:
    """Process referral code if present in command args."""
    if not command.args or not command.args.startswith("ref_"):
        return

    referral_code = command.args[4:]  # Remove "ref_" prefix
    await process_referral(
        ProcessReferralInputDTO(
            new_user_id=user_id,
            referral_code=referral_code,
        )
    )


async def _start_onboarding(
    message: Message,
    i18n: TranslatorRunner,
) -> None:
    """Start onboarding by asking user to select language."""
    await message.answer(
        text=i18n.get("onboarding-language"),
        reply_markup=get_onboarding_language_keyboard(),
    )


@router.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    command: CommandObject,
    process_referral: FromDishka[ProcessReferralInteractor],
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
) -> None:
    """Handle /start command — show main menu."""
    logger.info("User %s sent /start (is_new=%s)", message.from_user.id, user.is_new)
    if user.is_new:
        # Process referral for new users only
        await _process_referral_if_applicable(
            message.from_user.id, command, process_referral
        )
        # New users: show onboarding language selection
        await _start_onboarding(message, i18n)
        return

    await message.answer(
        text=i18n.get("welcome", name=user.first_name if user else "User"),
        reply_markup=get_main_menu_keyboard(i18n),
    )


@router.message(Command("help"))
async def command_help_handler(
    message: Message,
    i18n: TranslatorRunner,
) -> None:
    """Handle /help command."""
    logger.info("User %s sent /help", message.from_user.id)
    await message.answer(text=i18n.get("help-text"))


@router.callback_query(F.data == MainMenuCBData.menu)
async def cb_main_menu_handler(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: CreateUserOutputDTO,
) -> None:
    logger.info("User %s returned to main menu", callback.from_user.id)
    await callback.message.edit_text(
        text=i18n.get("welcome", name=user.first_name if user else "User"),
        reply_markup=get_main_menu_keyboard(i18n),
    )
    await callback.answer()
