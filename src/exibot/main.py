"""Точка входа Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from exibot.config.settings import load_settings
from exibot.core.logging_config import setup_logging
from exibot.handlers.art import create_art_router
from exibot.repositories.images import ImagesRepository

logger = logging.getLogger(__name__)


async def main() -> None:
    """Создать зависимости приложения и запустить Telegram polling."""
    settings = load_settings()
    setup_logging(settings.log_level)

    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()

    images_repository = ImagesRepository(settings.data_dir)
    art_router = create_art_router(images_repository)

    dispatcher.include_router(art_router)

    logger.info("Бот запущен")

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
