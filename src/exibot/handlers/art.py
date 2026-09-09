"""Обработчики загрузки и выдачи артов."""

import logging
import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from exibot.repositories.images import ImagesRepository

logger = logging.getLogger(__name__)


def create_art_router(images_repository: ImagesRepository) -> Router:
    """Создать роутер для работы с артами."""
    router = Router(name=__name__)

    @router.message(F.photo)
    async def save_photo(message: Message) -> None:
        """Сохранить file_id присланной или пересланной фотографии."""
        if not message.photo:
            return

        file_id = message.photo[-1].file_id

        if images_repository.add(file_id):
            logger.info("Сохранён новый арт: %s", file_id)
        else:
            logger.info("Арт уже есть в базе: %s", file_id)

    @router.message(F.document.mime_type.startswith("image/"))
    async def save_document(message: Message) -> None:
        """Сохранить изображение, присланное как документ."""
        document = message.document

        if (
            document is None
            or document.mime_type is None
            or not document.mime_type.startswith("image/")
        ):
            return

        if images_repository.add(document.file_id):
            logger.info("Сохранён новый арт-документ: %s", document.file_id)
        else:
            logger.info("Арт-документ уже есть в базе: %s", document.file_id)

    @router.message(Command("randomart"))
    async def random_art(message: Message) -> None:
        """Отправить случайный арт из локального хранилища."""
        images = images_repository.get_all()

        if not images:
            await message.answer("База пустая 😢 сначала добавь арты.")
            return

        file_id = random.choice(images)

        await message.answer_photo(
            file_id,
            caption="🎨 Лови артик!",
        )

        logger.info("Выдан случайный арт: %s", file_id)

    return router
