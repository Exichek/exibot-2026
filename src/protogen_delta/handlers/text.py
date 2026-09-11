"""Обработчик обычных текстовых сообщений."""

from aiogram import F, Router
from aiogram.types import Message

from protogen_delta.core.message_utils import split_message
from protogen_delta.services.response_engine import ResponseEngine


def create_text_router(response_engine: ResponseEngine) -> Router:
    """Создать роутер обычных текстовых сообщений."""
    router = Router(name=__name__)

    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        """Передать сообщение движку и отправить сформированный ответ."""
        if message.text is None:
            return

        if message.text.startswith("/"):
            return

        reply = await response_engine.respond(message.text)

        for chunk in split_message(reply):
            await message.answer(chunk)

    return router
