"""Репозиторий изображений бота."""

from pathlib import Path
from typing import cast

from protogen_delta.repositories.json_file import JsonFileRepository

_IMAGES_KEY = "IMAGES"


class ImagesRepository:
    """Хранилище Telegram file_id сохранённых изображений."""

    def __init__(self, data_dir: Path) -> None:
        """Инициализировать хранилище изображений."""
        self._storage = JsonFileRepository(
            path=data_dir / "images.json",
            default_data={_IMAGES_KEY: []},
        )

    def get_all(self) -> list[str]:
        """Вернуть file_id всех сохранённых изображений."""
        data = self._storage.load()
        images = data.get(_IMAGES_KEY, [])

        if not isinstance(images, list) or not all(
            isinstance(file_id, str) for file_id in images
        ):
            raise TypeError("Поле IMAGES должно содержать список строк")

        return cast(list[str], images)

    def add(self, file_id: str) -> bool:
        """Добавить изображение и вернуть True, если его ещё не было."""
        images = self.get_all()

        if file_id in images:
            return False

        images.append(file_id)
        self._storage.save({_IMAGES_KEY: images})
        return True

    def remove(self, file_id: str) -> bool:
        """Удалить изображение и вернуть True, если оно существовало."""
        images = self.get_all()

        if file_id not in images:
            return False

        images.remove(file_id)
        self._storage.save({_IMAGES_KEY: images})
        return True

    def count(self) -> int:
        """Вернуть количество сохранённых изображений."""
        return len(self.get_all())
