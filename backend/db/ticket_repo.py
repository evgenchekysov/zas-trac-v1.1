from uuid import UUID


class TicketRepo:
    async def get(self, ticket_id: UUID):
        """
        Возвращает заявку или None.
        """
        raise NotImplementedError

    async def update_status(self, ticket_id: UUID, status):
        """
        Обновляет статус заявки.
        """
        raise NotImplementedError

    async def is_participant(self, ticket_id: UUID, user_id: UUID) -> bool:
        """
        Проверяет, является ли пользователь участником заявки.
        """
        raise NotImplementedError
