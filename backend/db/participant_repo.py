from uuid import UUID
from typing import List


class ParticipantRepo:
    async def add(self, ticket_id: UUID, user_id: UUID):
        """
        Добавляет участника в заявку.
        """
        raise NotImplementedError

    async def remove(self, ticket_id: UUID, user_id: UUID):
        """
        Удаляет участника из заявки.
        """
        raise NotImplementedError

    async def list_by_ticket(self, ticket_id: UUID) -> List[UUID]:
        """
        Возвращает список участников заявки.
        """
        raise NotImplementedError
