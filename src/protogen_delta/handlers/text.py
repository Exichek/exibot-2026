"""Обработчик обычных текстовых сообщений."""

from time import monotonic

from aiogram import F, Router
from aiogram.types import Message

from protogen_delta.core.message_utils import split_message
from protogen_delta.services.response_engine import ResponseEngine

RATE_LIMIT_REPLY = "Слишком быстро :D Подожди пару секунд."


def create_text_router(
    response_engine: ResponseEngine,
    cooldown_seconds: float = 2.0,
) -> Router:
    """Создать роутер обычных текстовых сообщений."""
    router = Router(name=__name__)
    last_request_at: dict[int, float] = {}

    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        """Передать сообщение движку и отправить сформированный ответ."""
        if message.text is None:
            return

        if message.text.startswith("/"):
            return

        if message.from_user is not None:
            user_id = message.from_user.id
            now = monotonic()

            previous_request_at = last_request_at.get(user_id)

            if (
                previous_request_at is not None
                and now - previous_request_at < cooldown_seconds
            ):
                await message.answer(RATE_LIMIT_REPLY)
                return

            last_request_at[user_id] = now

        reply = await response_engine.respond(message.text)

        for chunk in split_message(reply):
            await message.answer(chunk)

    return router
