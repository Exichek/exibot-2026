"""Обнаружение фетишей и определение роли бота в RP."""

import logging
from typing import Literal

from protogen_delta.services.deepseek import DeepSeekService

logger = logging.getLogger(__name__)

FetishTriggers = dict[str, list[str]]
FetishRole = Literal["active", "passive", "unknown"]


def detect_fetishes(
    user_message: str,
    triggers: FetishTriggers,
) -> list[str]:
    """Найти фетиши по ключевым словам в сообщении пользователя."""
    text = user_message.lower()
    found: list[str] = []

    for fetish, keywords in triggers.items():
        if any(keyword.lower() in text for keyword in keywords):
            found.append(fetish)

    return found


class FetishRoleClassifier:
    """Определять роль бота в RP через DeepSeek."""

    def __init__(
        self,
        deepseek: DeepSeekService,
        prompt: str,
    ) -> None:
        """Инициализировать классификатор роли."""
        if not prompt.strip():
            raise ValueError("Промпт классификации роли фетиша не может быть пустым")

        self._deepseek = deepseek
        self._prompt = prompt

    async def classify(self, user_message: str) -> FetishRole:
        """Определить роль бота относительно действий пользователя."""
        try:
            result = await self._deepseek.classify(
                self._prompt,
                user_message,
            )
        except Exception:
            logger.exception("Ошибка определения роли фетиша")
            return "unknown"

        logger.info("Классификация роли фетиша: %s", result)

        if result == "active":
            return "active"

        if result == "passive":
            return "passive"

        return "unknown"
