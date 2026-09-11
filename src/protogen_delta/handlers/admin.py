"""Админские команды Telegram-бота."""

import asyncio
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from protogen_delta.core.state import BotState
from protogen_delta.repositories.images import ImagesRepository
from protogen_delta.repositories.users import UsersRepository


def create_admin_router(
    images_repository: ImagesRepository,
    users_repository: UsersRepository,
    bot_state: BotState,
    admin_ids: frozenset[int],
) -> Router:
    """Создать роутер административных команд."""
    router = Router(name=__name__)

    def is_admin(message: Message) -> bool:
        """Проверить, принадлежит ли сообщение администратору."""
        return message.from_user is not None and message.from_user.id in admin_ids

    async def deny_access(message: Message) -> None:
        """Сообщить пользователю об отсутствии доступа."""
        await message.answer("⛔ У тебя нет доступа к этой команде.")

    @router.message(Command("listimages"))
    async def list_images(message: Message) -> None:
        """Показать последние сохранённые арты."""
        if not is_admin(message):
            await deny_access(message)
            return

        images = images_repository.get_all()

        if not images:
            await message.answer("📂 База артов пуста.")
            return

        text = message.text or ""
        parts = text.strip().split(maxsplit=1)

        count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        count = max(1, min(count, 200))

        last_images = images[-count:][::-1]

        await message.answer(f"📂 Показываю последние {len(last_images)} артов:")

        for file_id in last_images:
            try:
                await message.answer_photo(
                    file_id,
                    caption=f"<code>{file_id}</code>",
                    parse_mode="HTML",
                )
                await asyncio.sleep(1)
            except Exception as error:
                await message.answer(f"⚠️ Ошибка с {file_id}: {error}")

    @router.message(Command("removeimage"))
    async def remove_image(message: Message) -> None:
        """Удалить арты по Telegram file_id."""
        if not is_admin(message):
            await deny_access(message)
            return

        text = message.text or ""
        parts = text.strip().split(maxsplit=1)

        if len(parts) < 2:
            await message.answer(
                "⚠️ Укажи ID артов через запятую.\n" "Пример: /removeimage id1,id2,id3"
            )
            return

        ids_to_remove = [
            file_id.strip() for file_id in parts[1].split(",") if file_id.strip()
        ]

        removed = 0
        not_found = 0

        for file_id in ids_to_remove:
            if images_repository.remove(file_id):
                removed += 1
            else:
                not_found += 1

        reply: list[str] = []

        if removed:
            reply.append(f"✅ Удалено: {removed} артов")

        if not_found:
            reply.append(f"⚠️ Не найдено: {not_found} артов")

        await message.answer("\n".join(reply) if reply else "⚠️ Ничего не удалено.")

    @router.message(Command("artcount"))
    async def art_count(message: Message) -> None:
        """Показать количество сохранённых артов."""
        if not is_admin(message):
            await deny_access(message)
            return

        count = images_repository.count()

        if count == 0:
            await message.answer("📂 База артов пуста.")
            return

        await message.answer(f"📂 В базе {count} артов.")

    @router.message(Command("status"))
    async def status(message: Message) -> None:
        """Показать состояние текущего процесса бота."""
        if not is_admin(message):
            await deny_access(message)
            return

        uptime = int(time.time() - bot_state.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60

        reply = (
            "📊 Статус бота:\n"
            f"• Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}\n"
            f"• Пользователей: {users_repository.count()}\n"
            f"• Ответов отправлено: {bot_state.reply_count}\n"
            f"• Настроение: {bot_state.mood}"
        )

        await message.answer(reply)

    @router.message(Command("ownhelp"))
    async def own_help(message: Message) -> None:
        """Показать список административных команд."""
        if not is_admin(message):
            await deny_access(message)
            return

        help_text = (
            "📖 Админские команды:\n\n"
            "/listimages <N> — показать последние N артов\n"
            "/removeimage <id1,id2,...> — удалить арты по ID\n"
            "/artcount — показать количество артов\n"
            "/status — показать статус бота\n"
            "/ping — проверить доступность\n"
            "/ownhelp — показать эту справку"
        )

        await message.answer(help_text)

    @router.message(Command("ping"))
    async def ping(message: Message) -> None:
        """Проверить доступность административного роутера."""
        if not is_admin(message):
            await deny_access(message)
            return

        await message.answer("🏓 Pong от админского роутера!")

    return router
