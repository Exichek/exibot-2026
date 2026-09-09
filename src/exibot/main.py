"""Точка входа Telegram-бота."""

import asyncio
import logging
from typing import cast

from aiogram import Bot, Dispatcher

from exibot.config.json_loader import load_json
from exibot.config.prompt_loader import load_prompt
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
from exibot.services.deepseek import DeepSeekService
from exibot.services.emotes import EmoteCategories
from exibot.services.insults import InsultClassifier

logger = logging.getLogger(__name__)


async def main() -> None:
    """Создать зависимости приложения и запустить Telegram polling."""
    settings = load_settings()
    setup_logging(settings.log_level)

    bot = Bot(token=settings.telegram_token)
    deepseek: DeepSeekService | None = None

    try:
        dispatcher = Dispatcher()

        images_repository = ImagesRepository(settings.data_dir)
        users_repository = UsersRepository(settings.data_dir)
        bot_state = BotState()

        start_data = load_json("start_messages.json")
        start_messages_raw = start_data.get("START_MESSAGES", [])

        if not isinstance(start_messages_raw, list) or not all(
            isinstance(message, str) for message in start_messages_raw
        ):
            raise TypeError("START_MESSAGES должен содержать список строк")

        start_messages = cast(list[str], start_messages_raw)

        personality_data = load_json("personality.json")

        greetings_raw = personality_data.get("GREETINGS", [])
        insults_raw = personality_data.get("INSULTS", [])

        if not isinstance(greetings_raw, list) or not all(
            isinstance(greeting, str) for greeting in greetings_raw
        ):
            raise TypeError("GREETINGS должен содержать список строк")

        if not isinstance(insults_raw, list) or not all(
            isinstance(insult, str) for insult in insults_raw
        ):
            raise TypeError("INSULTS должен содержать список строк")

        greetings = cast(list[str], greetings_raw)
        insults = cast(list[str], insults_raw)

        question_insult_data = load_json("question_insult_replies.json")
        question_insult_replies_raw = question_insult_data.get(
            "QUESTION_INSULT_REPLIES",
            [],
        )

        if not isinstance(question_insult_replies_raw, list) or not all(
            isinstance(reply, str) for reply in question_insult_replies_raw
        ):
            raise TypeError("QUESTION_INSULT_REPLIES должен содержать список строк")

        question_insult_replies = cast(
            list[str],
            question_insult_replies_raw,
        )

        emotes_data = load_json("emotes.json")
        emote_categories_raw = emotes_data.get("CATEGORIES", {})

        if not isinstance(emote_categories_raw, dict) or not all(
            isinstance(category, str)
            and isinstance(emotes, list)
            and all(isinstance(emote, str) for emote in emotes)
            for category, emotes in emote_categories_raw.items()
        ):
            raise TypeError("CATEGORIES должен содержать словарь списков строк")

        emote_categories = cast(
            EmoteCategories,
            emote_categories_raw,
        )

        insult_prompt = load_prompt("insult_classification.txt")

        deepseek = DeepSeekService(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
        )

        insult_classifier = InsultClassifier(
            deepseek=deepseek,
            prompt=insult_prompt,
        )

        start_router = create_start_router(
            users_repository,
            start_messages,
        )
        help_router = create_help_router()
        art_router = create_art_router(images_repository)
        unknown_command_router = create_unknown_command_router()
        text_router = create_text_router(
            bot_state=bot_state,
            greetings=greetings,
            insult_classifier=insult_classifier,
            insults=insults,
            question_insult_replies=question_insult_replies,
            emote_categories=emote_categories,
        )

        dispatcher.include_router(start_router)
        dispatcher.include_router(help_router)
        dispatcher.include_router(art_router)
        dispatcher.include_router(unknown_command_router)
        dispatcher.include_router(text_router)

        await set_commands(bot)

        logger.info("Бот запущен")

        await dispatcher.start_polling(bot)
    finally:
        try:
            if deepseek is not None:
                await deepseek.close()
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
