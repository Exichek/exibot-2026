"""Определение коротких приветствий пользователя."""

import re

GREETINGS = {
    "привет",
    "ку",
    "здаров",
    "йоу",
    "здравствуй",
    "кулити",
    "хай",
    "куку",
    "прив",
    "hi",
    "hello",
    "hey",
    "yo",
    "sup",
    "yoho",
}


def is_greeting(text: str) -> bool:
    """Проверить, является ли сообщение одиночным приветствием."""
    words: list[str] = re.findall(r"\w+", text.lower())

    if len(words) != 1:
        return False

    word = words[0]

    if word in GREETINGS:
        return True

    if word.startswith(("прив", "привет")):
        return True

    if word.startswith(("здаров", "здоров")):
        return True

    return word.startswith(("yo", "sup"))
