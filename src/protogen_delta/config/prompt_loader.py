"""Загрузка текстовых промптов приложения."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(filename: str) -> str:
    """Загрузить текстовый промпт из каталога prompts."""
    path = PROMPTS_DIR / filename

    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл промпта не найден: {path}") from None
