"""Точка входа Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from exibot.config.json_loader import load_json
from exibot.config.settings import load_settings
from exibot.core.logging_config import setup_logging
from exibot.core.state import BotState
from exibot.core.telegram_commands import set_commands
from exibot.handlers.art import create_art_router
from exibot.handlers.help import create_help_router
from exibot.handlers.start import create_start_router
from exibot.handlers.text import create_text_router
from exibot.handlers.unknown_command import create_unknown_command_router
from exibot.repositories.images import ImagesRepository
from exibot.repositories.users import UsersRepository

logger = logging.getLogger(__name__)


async def main() -> None:
    """Создать зависимости приложения и запустить Telegram polling."""
    settings = load_settings()
    setup_logging(settings.log_level)

    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()

    await set_commands(bot)

    images_repository = ImagesRepository(settings.data_dir)
    users_repository = UsersRepository(settings.data_dir)
    bot_state = BotState()

    start_data = load_json("start_messages.json")
    start_messages = start_data.get("START_MESSAGES", [])

    if not isinstance(start_messages, list) or not all(
        isinstance(message, str) for message in start_messages
    ):
        raise TypeError("START_MESSAGES должен содержать список строк")

    personality_data = load_json("personality.json")
    greetings = personality_data.get("GREETINGS", [])

    if not isinstance(greetings, list) or not all(
        isinstance(greeting, str) for greeting in greetings
    ):
        raise TypeError("GREETINGS должен содержать список строк")

    start_router = create_start_router(
        users_repository,
        start_messages,
    )
    help_router = create_help_router()
    art_router = create_art_router(images_repository)
    unknown_command_router = create_unknown_command_router()
    text_router = create_text_router(
        bot_state,
        greetings,
    )

    dispatcher.include_router(start_router)
    dispatcher.include_router(help_router)
    dispatcher.include_router(art_router)
    dispatcher.include_router(unknown_command_router)
    dispatcher.include_router(text_router)

    logger.info("Бот запущен")

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
