"""Загрузка статических JSON-конфигов приложения."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_DATA_DIR = Path(__file__).resolve().parent / "data"


def load_json(filename: str) -> dict[str, Any]:
    """Загрузить JSON-конфиг из каталога статических данных."""
    path = CONFIG_DATA_DIR / filename

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.exception("Файл конфигурации не найден: %s", path)
        raise
    except json.JSONDecodeError:
        logger.exception("Ошибка чтения JSON-конфига: %s", path)
        raise

    if not isinstance(data, dict):
        raise TypeError(f"Корневой элемент JSON-конфига должен быть объектом: {path}")

    return data
