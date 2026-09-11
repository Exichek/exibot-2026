"""Тесты простых сервисов обработки текста."""

from protogen_delta.services.emotes import ends_with_emote, pick_emote
from protogen_delta.services.fetishes import detect_fetishes
from protogen_delta.services.greetings import is_greeting


def test_is_greeting_recognizes_known_greeting() -> None:
    """Известное одиночное приветствие должно распознаваться."""
    assert is_greeting("привет") is True


def test_is_greeting_ignores_case_and_punctuation() -> None:
    """Регистр и знаки препинания не должны мешать приветствию."""
    assert is_greeting("ПрИвЕт!!!") is True


def test_is_greeting_recognizes_prefixes() -> None:
    """Расширенные формы известных приветствий должны распознаваться."""
    assert is_greeting("приветик") is True
    assert is_greeting("здарова") is True


def test_is_greeting_rejects_multiple_words() -> None:
    """Сообщение из нескольких слов не должно считаться быстрым приветствием."""
    assert is_greeting("привет как дела") is False


def test_pick_emote_returns_emote_from_category() -> None:
    """Эмоут должен выбираться из указанной категории."""
    categories = {
        "NORMAL": ["UwU"],
    }

    assert pick_emote(categories, "normal") == "UwU"


def test_pick_emote_returns_empty_string_for_missing_category() -> None:
    """Для отсутствующей категории должен возвращаться пустой текст."""
    categories = {
        "NORMAL": ["UwU"],
    }

    assert pick_emote(categories, "missing") == ""


def test_ends_with_emote_detects_known_emote() -> None:
    """Известный эмоут в конце сообщения должен обнаруживаться."""
    categories = {
        "NORMAL": ["UwU", "^w^"],
        "BLUSH": [">///<"],
    }

    assert ends_with_emote("Приветик UwU", categories) is True


def test_ends_with_emote_returns_false_without_emote() -> None:
    """Обычный текст не должен считаться заканчивающимся эмоутом."""
    categories = {
        "NORMAL": ["UwU"],
    }

    assert ends_with_emote("Обычный ответ", categories) is False


def test_detect_fetishes_finds_multiple_matches() -> None:
    """В одном сообщении должны находиться все подходящие категории."""
    triggers = {
        "bondage": ["верёвка", "связал"],
        "oral": ["минет"],
        "public": ["публично"],
    }

    result = detect_fetishes(
        "Связал тебя верёвкой и сделал минет",
        triggers,
    )

    assert result == ["bondage", "oral"]


def test_detect_fetishes_is_case_insensitive() -> None:
    """Поиск ключевых слов не должен зависеть от регистра."""
    triggers = {
        "bondage": ["связал"],
    }

    result = detect_fetishes(
        "Я ТЕБЯ СВЯЗАЛ",
        triggers,
    )

    assert result == ["bondage"]
