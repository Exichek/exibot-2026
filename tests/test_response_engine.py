"""Тесты движка формирования ответов."""

import asyncio
from typing import cast
from unittest.mock import AsyncMock

import pytest

import exibot.services.response_engine as response_engine_module
from exibot.core.state import BotState
from exibot.services.deepseek import DeepSeekService
from exibot.services.fetishes import FetishRoleClassifier
from exibot.services.insults import InsultClassifier
from exibot.services.mood import MoodClassifier
from exibot.services.response_engine import (
    ResponseEngine,
    ResponseEngineConfig,
)


def _create_engine() -> tuple[
    ResponseEngine,
    BotState,
    AsyncMock,
    AsyncMock,
    AsyncMock,
    AsyncMock,
]:
    """Создать движок с моками всех внешних сервисов."""
    deepseek_mock = AsyncMock(spec=DeepSeekService)
    insult_mock = AsyncMock(spec=InsultClassifier)
    mood_mock = AsyncMock(spec=MoodClassifier)
    role_mock = AsyncMock(spec=FetishRoleClassifier)

    deepseek_mock.chat.return_value = "Ответ"
    insult_mock.classify.return_value = "none"
    mood_mock.classify.return_value = "playful"
    role_mock.classify.return_value = "unknown"

    state = BotState()

    config = ResponseEngineConfig(
        greetings=["Приветик"],
        insults=["Отвали"],
        question_insult_replies=["Сам такой вопрос задаёшь?"],
        horny_replies=["Horny reply"],
        moods={
            "playful": [],
            "sweet": [],
            "horny": [],
            "angry": [],
        },
        fetish_triggers={
            "bondage": ["связал"],
        },
        fetish_names={
            "bondage": "бондаж",
        },
        emote_categories={
            "NORMAL": ["UwU"],
            "BLUSH": [">///<"],
            "INSULT": [">:("],
        },
        system_prompt="SYSTEM PROMPT",
        rp_prompt="RP PROMPT",
    )

    engine = ResponseEngine(
        deepseek=cast(DeepSeekService, deepseek_mock),
        insult_classifier=cast(InsultClassifier, insult_mock),
        mood_classifier=cast(MoodClassifier, mood_mock),
        fetish_role_classifier=cast(
            FetishRoleClassifier,
            role_mock,
        ),
        bot_state=state,
        config=config,
    )

    return (
        engine,
        state,
        deepseek_mock,
        insult_mock,
        mood_mock,
        role_mock,
    )


def test_response_engine_returns_greeting_without_deepseek() -> None:
    """Одиночное приветствие не должно отправляться в DeepSeek."""
    (
        engine,
        state,
        deepseek_mock,
        insult_mock,
        _,
        _,
    ) = _create_engine()

    result = asyncio.run(
        engine.respond("Привет!"),
    )

    assert result == "Приветик"
    assert state.reply_count == 1

    insult_mock.classify.assert_not_awaited()
    deepseek_mock.chat.assert_not_awaited()


def test_response_engine_returns_direct_insult_without_chat() -> None:
    """Прямое оскорбление должно получать быстрый локальный ответ."""
    (
        engine,
        state,
        deepseek_mock,
        insult_mock,
        mood_mock,
        _,
    ) = _create_engine()

    insult_mock.classify.return_value = "direct"

    result = asyncio.run(
        engine.respond("Ты идиот"),
    )

    assert result == "Отвали >:("
    assert state.reply_count == 1

    mood_mock.classify.assert_not_awaited()
    deepseek_mock.chat.assert_not_awaited()


def test_response_engine_updates_mood_and_calls_chat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Обычное сообщение должно обновить настроение и вызвать DeepSeek."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        mood_mock,
        role_mock,
    ) = _create_engine()

    mood_mock.classify.return_value = "sweet"
    deepseek_mock.chat.return_value = "Обычный ответ"

    result = asyncio.run(
        engine.respond("Как дела?"),
    )

    assert result == "Обычный ответ"
    assert state.mood == "sweet"
    assert state.reply_count == 1

    deepseek_mock.chat.assert_awaited_once_with(
        system_prompt="SYSTEM PROMPT",
        user_message="Как дела?",
    )

    role_mock.classify.assert_not_awaited()


def test_response_engine_uses_rp_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RP-сообщение должно использовать RP-промпт."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        _,
        role_mock,
    ) = _create_engine()

    deepseek_mock.chat.return_value = "RP ответ"

    result = asyncio.run(
        engine.respond("*обнял тебя*"),
    )

    assert result == "RP ответ"
    assert state.reply_count == 1

    role_mock.classify.assert_not_awaited()

    call = deepseek_mock.chat.await_args

    assert call is not None

    prompt = call.kwargs["system_prompt"]

    assert prompt.startswith("RP PROMPT")
    assert "ВАЖНО" in prompt
    assert "фиолетовая футболка" in prompt


def test_response_engine_adds_fetish_context_and_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Фетиш и роль должны добавляться в динамический RP-промпт."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        _,
        role_mock,
    ) = _create_engine()

    role_mock.classify.return_value = "active"
    deepseek_mock.chat.return_value = "RP ответ"

    result = asyncio.run(
        engine.respond("*связал тебя*"),
    )

    assert result == "RP ответ"
    assert state.reply_count == 1

    role_mock.classify.assert_awaited_once_with(
        "*связал тебя*",
    )

    call = deepseek_mock.chat.await_args

    assert call is not None

    prompt = call.kwargs["system_prompt"]

    assert "бондаж (бот актив)" in prompt
    assert "Отыгрывай их в ролевке" in prompt
    assert "активного партнёра" in prompt


def test_response_engine_does_not_classify_role_without_fetish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Без найденного фетиша отдельная классификация роли не нужна."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        _,
        _,
        _,
        _,
        role_mock,
    ) = _create_engine()

    asyncio.run(
        engine.respond("*погладил тебя*"),
    )

    role_mock.classify.assert_not_awaited()


def test_response_engine_returns_fallback_on_chat_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ошибка обычного запроса DeepSeek должна дать аварийный ответ."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        _,
        _,
    ) = _create_engine()

    deepseek_mock.chat.side_effect = RuntimeError("API error")

    result = asyncio.run(
        engine.respond("Как дела"),
    )

    assert result == "Бля, у тостера что-то сломалось... ≧◡≦"
    assert state.reply_count == 0


def test_response_engine_handles_empty_deepseek_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Пустой ответ DeepSeek должен заменяться понятным сообщением."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        _,
        _,
    ) = _create_engine()

    deepseek_mock.chat.return_value = ""

    result = asyncio.run(
        engine.respond("Обычное сообщение"),
    )

    assert result == "Пустой ответ от DeepSeek"
    assert state.reply_count == 1


def test_response_engine_handles_whitespace_deepseek_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ответ только из пробелов должен считаться молчанием модели."""
    monkeypatch.setattr(
        response_engine_module.random,
        "random",
        lambda: 1.0,
    )

    (
        engine,
        state,
        deepseek_mock,
        _,
        _,
        _,
    ) = _create_engine()

    deepseek_mock.chat.return_value = "   "

    result = asyncio.run(
        engine.respond("Обычное сообщение"),
    )

    assert result == "DeepSeek промолчал..."
    assert state.reply_count == 1


def test_response_engine_rejects_empty_system_prompt() -> None:
    """Пустой системный промпт должен запрещать создание движка."""
    deepseek_mock = AsyncMock(spec=DeepSeekService)
    insult_mock = AsyncMock(spec=InsultClassifier)
    mood_mock = AsyncMock(spec=MoodClassifier)
    role_mock = AsyncMock(spec=FetishRoleClassifier)

    config = ResponseEngineConfig(
        greetings=[],
        insults=[],
        question_insult_replies=[],
        horny_replies=[],
        moods={},
        fetish_triggers={},
        fetish_names={},
        emote_categories={},
        system_prompt="   ",
        rp_prompt="RP",
    )

    with pytest.raises(
        ValueError,
        match="Системный промпт",
    ):
        ResponseEngine(
            deepseek=cast(DeepSeekService, deepseek_mock),
            insult_classifier=cast(
                InsultClassifier,
                insult_mock,
            ),
            mood_classifier=cast(
                MoodClassifier,
                mood_mock,
            ),
            fetish_role_classifier=cast(
                FetishRoleClassifier,
                role_mock,
            ),
            bot_state=BotState(),
            config=config,
        )
