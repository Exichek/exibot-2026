"""Тесты простых Telegram-обработчиков."""

import asyncio
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram import Router
from aiogram.types import Message

import protogen_delta.handlers.unknown_command as unknown_command_module
from protogen_delta.handlers.help import HELP_TEXT, create_help_router
from protogen_delta.handlers.text import create_text_router
from protogen_delta.handlers.unknown_command import (
    UNKNOWN_COMMAND_REPLIES,
    create_unknown_command_router,
)
from protogen_delta.services.response_engine import ResponseEngine


def _create_message_mock(
    text: str | None = None,
) -> tuple[Message, AsyncMock, AsyncMock]:
    """Создать Message с асинхронными методами answer и reply."""
    message_mock = Mock(spec=Message)

    message_mock.text = text

    answer_mock = AsyncMock()
    reply_mock = AsyncMock()

    message_mock.answer = answer_mock
    message_mock.reply = reply_mock

    return (
        cast(Message, message_mock),
        answer_mock,
        reply_mock,
    )


async def _call_first_handler(
    router: Router,
    message: Message,
) -> None:
    """Вызвать первый зарегистрированный message-handler роутера."""
    handler = router.message.handlers[0]

    await handler.callback(message)


def test_help_handler_sends_help_text() -> None:
    """Команда /help должна отправлять текст справки."""
    router = create_help_router()

    message, answer_mock, _ = _create_message_mock()

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    answer_mock.assert_awaited_once_with(
        HELP_TEXT,
    )


def test_unknown_command_handler_sends_known_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Неизвестная команда должна получать одну из стандартных реплик."""
    router = create_unknown_command_router()

    monkeypatch.setattr(
        unknown_command_module.random,
        "choice",
        lambda values: values[0],
    )

    message, _, reply_mock = _create_message_mock()

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    reply_mock.assert_awaited_once_with(
        UNKNOWN_COMMAND_REPLIES[0],
    )


def test_text_handler_calls_response_engine() -> None:
    """Обычный текст должен передаваться движку ответов."""
    engine_mock = AsyncMock(spec=ResponseEngine)
    engine_mock.respond.return_value = "Ответ бота"

    router = create_text_router(
        cast(ResponseEngine, engine_mock),
    )

    message, answer_mock, _ = _create_message_mock("Привет, как дела?")

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    engine_mock.respond.assert_awaited_once_with(
        "Привет, как дела?",
    )
    answer_mock.assert_awaited_once_with(
        "Ответ бота",
    )


def test_text_handler_splits_long_response() -> None:
    """Длинный ответ должен отправляться несколькими сообщениями."""
    engine_mock = AsyncMock(spec=ResponseEngine)
    engine_mock.respond.return_value = "a" * 5000

    router = create_text_router(
        cast(ResponseEngine, engine_mock),
    )

    message, answer_mock, _ = _create_message_mock("Сообщение")

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    assert answer_mock.await_count == 2


def test_text_handler_ignores_commands() -> None:
    """Команды не должны попадать в обычный текстовый движок."""
    engine_mock = AsyncMock(spec=ResponseEngine)

    router = create_text_router(
        cast(ResponseEngine, engine_mock),
    )

    message, answer_mock, _ = _create_message_mock("/something")

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    engine_mock.respond.assert_not_awaited()
    answer_mock.assert_not_awaited()


def test_text_handler_ignores_missing_text() -> None:
    """Сообщение без текста не должно обрабатываться."""
    engine_mock = AsyncMock(spec=ResponseEngine)

    router = create_text_router(
        cast(ResponseEngine, engine_mock),
    )

    message, answer_mock, _ = _create_message_mock(None)

    asyncio.run(
        _call_first_handler(
            router,
            message,
        )
    )

    engine_mock.respond.assert_not_awaited()
    answer_mock.assert_not_awaited()
