"""Обработчик обычных текстовых сообщений."""

import random

from aiogram import F, Router
from aiogram.types import Message

from exibot.core.message_utils import split_message
from exibot.core.state import BotState
from exibot.services.greetings import is_greeting


def create_text_router(
    bot_state: BotState,
    greetings: list[str],
) -> Router:
    """Создать роутер обычных текстовых сообщений."""
    router = Router(name=__name__)

    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        """Обработать обычное текстовое сообщение пользователя."""
        if message.text is None:
            return

        if message.text.startswith("/"):
            return

        if is_greeting(message.text) and greetings:
            reply = random.choice(greetings)
            bot_state.register_reply()

            for chunk in split_message(reply):
                await message.answer(chunk)

    return router
