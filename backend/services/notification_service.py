"""
ZAS-TRAC — Notification Service
==============================

Слой уведомлений (Telegram, email, webhooks).

На ДНЕ 29:
- только контракт
- без конкретных каналов
"""

NOTIFICATIONS = [
    "ticket_created",
    "ticket_assigned",
    "ticket_done",
    "ticket_closed",
]


async def notify(
    notification_type: str,
    user_ids: list[str],
    payload: dict | None = None,
):
    """
    Асинхронно уведомляет пользователей.

    Реализация каналов добавляется позже.
    """
    raise NotImplementedError
