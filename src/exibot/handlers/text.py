"""Обработчик обычных текстовых сообщений."""

import random

from aiogram import F, Router
from aiogram.types import Message

from exibot.core.message_utils import split_message
from exibot.core.state import BotState
from exibot.services.emotes import EmoteCategories, pick_emote
from exibot.services.greetings import is_greeting
from exibot.services.insults import InsultClassifier


def create_text_router(
    bot_state: BotState,
    greetings: list[str],
    insult_classifier: InsultClassifier,
    insults: list[str],
    question_insult_replies: list[str],
    emote_categories: EmoteCategories,
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

        user_message = message.text

        if is_greeting(user_message) and greetings:
            reply = random.choice(greetings)
            bot_state.register_reply()

            for chunk in split_message(reply):
                await message.answer(chunk)

            return

        insult_type = await insult_classifier.classify(user_message)

        if insult_type == "question" and question_insult_replies:
            reply = random.choice(question_insult_replies)
            emote = pick_emote(emote_categories, "BLUSH")
            bot_state.register_reply()

            for chunk in split_message(f"{reply} {emote}".rstrip()):
                await message.answer(chunk)

            return

        if insult_type == "direct" and insults:
            reply = random.choice(insults)
            emote = pick_emote(emote_categories, "INSULT")
            bot_state.register_reply()

            for chunk in split_message(f"{reply} {emote}".rstrip()):
                await message.answer(chunk)

            return

        if insult_type == "general" and insults:
            reply = random.choice(insults)
            bot_state.register_reply()

            for chunk in split_message(reply):
                await message.answer(chunk)

            return

    return router
