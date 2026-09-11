"""Состояние бота во время работы приложения."""

import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class BotState:
    """Хранить изменяемое состояние текущего процесса бота."""

    reply_count: int = 0
    mood: str = "playful"
    start_time: float = field(default_factory=time.time)

    def register_reply(self) -> None:
        """Увеличить счётчик отправленных ботом ответов."""
        self.reply_count += 1
