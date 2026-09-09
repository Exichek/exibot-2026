"""Работа с текстовыми эмоутами бота."""

import random

EmoteCategories = dict[str, list[str]]


def pick_emote(
    categories: EmoteCategories,
    category: str,
) -> str:
    """Вернуть случайный эмоут из указанной категории."""
    emotes = categories.get(category.upper(), [])

    if not emotes:
        return ""

    return random.choice(emotes)


def ends_with_emote(
    text: str,
    categories: EmoteCategories,
) -> bool:
    """Проверить, заканчивается ли текст одним из известных эмоутов."""
    stripped_text = text.strip()

    for emotes in categories.values():
        if any(stripped_text.endswith(emote) for emote in emotes):
            return True

    return False
