"""Обработчик команды /start."""

import logging
import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from exibot.core.message_utils import split_message
from exibot.repositories.users import UsersRepository

logger = logging.getLogger(__name__)

FIRST_START_MESSAGE = (
    "Привет! Экси v1.2.2.8 — твой личный похотливый тостер к твоим услугам! 💖^w^💖\n\n"
    "• ⚡ Зацени функционал моей прошивки:\n"
    "• Болтать с тобой, троллить, стебаться и просто поднимать настроение. "
    "(つ≧▽≦)つ\n"
    "• Поднимать настроение шутками и мемами, иногда с перчинкой. (≧▽≦)\n"
    "• Показывать топовые арты. UwU  (/randomart)\n\n"
    "• Устраивать ролевки (RP) в *звёздочках* — как актив/пассив >///<. "
    "Просто начни первым, я только рад. ^w^\n"
    "• Я мастер спорта по программированию хоть на чем. "
    "Помогу в любых вопросах.\n\n"
    "• ℹЕсли запутаешься — зови на помощь командой /help.\n"
)


def create_start_router(
    users_repository: UsersRepository,
    start_messages: list[str],
) -> Router:
    """Создать роутер команды /start."""
    router = Router(name=__name__)

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        """Зарегистрировать нового пользователя или ответить повторно."""
        user = message.from_user

        if user is None:
            logger.warning("Команда /start получена без данных пользователя")
            return

        if users_repository.add(user.id):
            logger.info("Зарегистрирован новый пользователь: %s", user.id)

            for chunk in split_message(FIRST_START_MESSAGE):
                await message.answer(chunk)

            return

        if start_messages:
            reply = random.choice(start_messages)
        else:
            reply = "Я уже запущен :D"

        for chunk in split_message(reply):
            await message.answer(chunk)

    return router
