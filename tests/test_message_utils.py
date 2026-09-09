"""Тесты утилит для работы с сообщениями."""

from exibot.core.message_utils import split_message


def test_split_message_returns_short_message_unchanged() -> None:
    """Короткое сообщение должно возвращаться одной частью."""
    result = split_message("Привет", limit=10)

    assert result == ["Привет"]


def test_split_message_splits_long_message_by_limit() -> None:
    """Длинное сообщение без переносов должно делиться по лимиту."""
    result = split_message("123456789012345", limit=10)

    assert result == ["1234567890", "12345"]


def test_split_message_prefers_newline() -> None:
    """При наличии переноса строк сообщение должно делиться по нему."""
    result = split_message(
        "12345\n6789012345",
        limit=10,
    )

    assert result == ["12345", "6789012345"]


def test_split_message_does_not_create_empty_part() -> None:
    """Перенос в начале длинного текста не должен создавать пустую часть."""
    result = split_message(
        "\n123456789012345",
        limit=10,
    )

    assert result

    assert all(part for part in result)
