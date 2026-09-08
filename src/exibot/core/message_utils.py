"""Утилиты для работы с сообщениями Telegram."""

TELEGRAM_MESSAGE_LIMIT = 4096


def split_message(
    text: str,
    limit: int = TELEGRAM_MESSAGE_LIMIT,
) -> list[str]:
    """Разбить длинный текст на части, не превышающие заданный лимит."""
    parts: list[str] = []

    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)

        if cut == -1:
            cut = limit

        parts.append(text[:cut])
        text = text[cut:].lstrip()

    if text:
        parts.append(text)

    return parts
