"""Работа с изменяемыми данными в JSON-файлах."""

import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class JsonFileRepository:
    """Базовый репозиторий для чтения и сохранения JSON-данных."""

    def __init__(
        self,
        path: Path,
        default_data: dict[str, Any],
    ) -> None:
        """Сохранить путь к файлу и начальную структуру данных."""
        self._path = path
        self._default_data = default_data

    def load(self) -> dict[str, Any]:
        """Загрузить данные или создать файл с начальными значениями."""
        if not self._path.exists():
            data = deepcopy(self._default_data)
            self.save(data)
            return data

        try:
            with self._path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            logger.exception(
                "Ошибка чтения JSON-файла: %s",
                self._path,
            )
            raise

        if not isinstance(data, dict):
            raise TypeError(
                f"Корневой элемент JSON-файла должен быть объектом: {self._path}"
            )

        return data

    def save(self, data: dict[str, Any]) -> None:
        """Сохранить данные в JSON-файл."""
        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
