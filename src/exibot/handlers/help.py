"""Обработчик команды /help."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

HELP_TEXT = (
    "📖 Команды бота:\n\n"
    "/start – 🚀 Запустить бота\n"
    "/randomart – 🎨 Случайный арт\n"
    "/help – ℹ️ Помощь (это сообщение)\n"
)


def create_help_router() -> Router:
    """Создать роутер команды /help."""
    router = Router(name=__name__)

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        """Отправить пользователю список доступных команд."""
        await message.answer(HELP_TEXT)

    return router
