import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_token: str
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"


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
    )
