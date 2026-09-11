"""Настройка логирования приложения."""

import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: str = "INFO") -> None:
    """Настроить единое логирование для всего приложения."""
    numeric_level = getattr(logging, level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Неизвестный уровень логирования: {level}")

    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
    )
