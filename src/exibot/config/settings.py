"""Настройки приложения и загрузка переменных окружения."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Настройки приложения, загружаемые из переменных окружения."""

    telegram_token: str
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    admin_ids: frozenset[int] = frozenset()


def _parse_admin_ids(value: str) -> frozenset[int]:
    """Преобразовать строку Telegram ID через запятую в множество чисел."""
    if not value.strip():
        return frozenset()

    try:
        return frozenset(
            int(user_id.strip()) for user_id in value.split(",") if user_id.strip()
        )
    except ValueError as error:
        raise ValueError(
            "ADMIN_IDS должен содержать Telegram ID через запятую"
        ) from error


def load_settings() -> Settings:
    """Загрузить настройки приложения из переменных окружения."""
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

    if not telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN не найден в окружении")

    if not deepseek_api_key:
        raise RuntimeError("DEEPSEEK_API_KEY не найден в окружении")

    return Settings(
        admin_ids=_parse_admin_ids(
            os.getenv("ADMIN_IDS", ""),
        ),
        telegram_token=telegram_token,
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=os.getenv(
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com",
        ),
        deepseek_model=os.getenv(
            "DEEPSEEK_MODEL",
            "deepseek-chat",
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
    )
