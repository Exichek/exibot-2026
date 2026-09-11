"""Глобальная обработка ошибок Telegram-бота."""

import logging

from aiogram import Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)


async def handle_error(event: ErrorEvent) -> None:
    """Обработать ошибку, возникшую при обработке Telegram update."""
    exception = event.exception

    if isinstance(exception, TelegramForbiddenError):
        logger.warning(
            "Пользователь заблокировал бота.",
        )
        return

    logger.error(
        "Необработанная ошибка при обработке Telegram update.",
        exc_info=(
            type(exception),
            exception,
            exception.__traceback__,
        ),
    )


def register_error_handler(dispatcher: Dispatcher) -> None:
    """Зарегистрировать глобальный обработчик ошибок."""
    dispatcher.errors.register(handle_error)
