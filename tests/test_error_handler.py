"""Тесты глобального обработчика ошибок."""

import asyncio
from typing import cast
from unittest.mock import Mock

import pytest
from aiogram import Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import ErrorEvent

import protogen_delta.handlers.errors as errors_module
from protogen_delta.handlers.errors import (
    handle_error,
    register_error_handler,
)


def _create_error_event(
    exception: Exception,
) -> ErrorEvent:
    """Создать минимальный ErrorEvent для тестов."""
    event_mock = Mock(spec=ErrorEvent)

    event_mock.exception = exception
    event_mock.update = "test-update"

    return cast(ErrorEvent, event_mock)


def test_handle_error_logs_forbidden_as_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Блокировка бота пользователем должна логироваться как warning."""
    warning_mock = Mock()
    error_mock = Mock()

    monkeypatch.setattr(
        errors_module.logger,
        "warning",
        warning_mock,
    )
    monkeypatch.setattr(
        errors_module.logger,
        "error",
        error_mock,
    )

    exception = TelegramForbiddenError(
        method=Mock(),
        message="Forbidden",
    )

    event = _create_error_event(exception)

    asyncio.run(handle_error(event))

    warning_mock.assert_called_once_with(
        "Пользователь заблокировал бота.",
    )
    error_mock.assert_not_called()


def test_handle_error_logs_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Неизвестная ошибка должна логироваться как error с traceback."""
    error_mock = Mock()

    monkeypatch.setattr(
        errors_module.logger,
        "error",
        error_mock,
    )

    exception = RuntimeError("boom")

    event = _create_error_event(exception)

    asyncio.run(handle_error(event))

    error_mock.assert_called_once()

    call = error_mock.call_args

    assert call is not None

    assert call.args == ("Необработанная ошибка при обработке Telegram update.",)

    assert call.kwargs["exc_info"][0] is RuntimeError
    assert call.kwargs["exc_info"][1] is exception


def test_register_error_handler_registers_callback() -> None:
    """Глобальный обработчик должен регистрироваться в Dispatcher."""
    dispatcher_mock = Mock(spec=Dispatcher)
    dispatcher_mock.errors = Mock()
    dispatcher_mock.errors.register = Mock()

    register_error_handler(
        cast(Dispatcher, dispatcher_mock),
    )

    dispatcher_mock.errors.register.assert_called_once_with(
        handle_error,
    )
