"""
ZAS-TRAC — Audit / Event Service
===============================

Сервис фиксации событий и действий пользователей.

Назначение:
- Вести ЖУРНАЛ всех значимых событий системы
- Используется для аудита, отладки, отчётов, уведомлений, Telegram

Реализация событий НЕ должна влиять на бизнес-логику.
Сбой логирования не должен ломать основную операцию.
"""

EVENTS = [
    "ticket_created",
    "ticket_status_changed",
    "ticket_joined",
    "ticket_left",
    "session_started",
    "session_stopped",
    "session_auto_paused",
    "ticket_done",
    "ticket_closed",
]


async def log_event(
    event_type: str,
    user_id: str,
    ticket_id: str | None = None,
    payload: dict | None = None,
):
    """
    Фиксирует событие в журнале.

    - event_type: тип события (см. EVENTS)
    - user_id: инициатор действия
    - ticket_id: связанная заявка (если есть)
    - payload: дополнительные данные
    """
    raise NotImplementedError
