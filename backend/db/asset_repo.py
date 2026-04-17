from uuid import UUID
from typing import Optional


class AssetRepo:
    async def get(self, asset_id: UUID):
        """
        Возвращает объект оборудования или None.
        """
        raise NotImplementedError

    async def find_by_code(self, code: str):
        """
        Поиск оборудования по коду / QR.
        """
        raise NotImplementedError
