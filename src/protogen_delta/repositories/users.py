"""Репозиторий пользователей бота."""

from pathlib import Path
from typing import cast

from protogen_delta.repositories.json_file import JsonFileRepository

_USERS_KEY = "USERS"


class UsersRepository:
    """Хранилище идентификаторов пользователей Telegram."""

    def __init__(self, data_dir: Path) -> None:
        """Инициализировать хранилище пользователей."""
        self._storage = JsonFileRepository(
            path=data_dir / "users.json",
            default_data={_USERS_KEY: []},
        )

    def get_all(self) -> list[int]:
        """Вернуть идентификаторы всех сохранённых пользователей."""
        data = self._storage.load()
        users = data.get(_USERS_KEY, [])

        if not isinstance(users, list) or not all(
            isinstance(user_id, int) for user_id in users
        ):
            raise TypeError("Поле USERS должно содержать список целых чисел")

        return cast(list[int], users)

    def add(self, user_id: int) -> bool:
        """Добавить пользователя и вернуть True, если его ещё не было."""
        users = self.get_all()

        if user_id in users:
            return False

        users.append(user_id)
        self._storage.save({_USERS_KEY: users})
        return True

    def count(self) -> int:
        """Вернуть количество сохранённых пользователей."""
        return len(self.get_all())
