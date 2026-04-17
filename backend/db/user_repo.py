class UserRepo:
    def __init__(self, db):
        self.db = db

    async def get(self, user_id: str):
        query = """
        SELECT id, full_name, created_at
        FROM users
        WHERE id = %s
        """
        return await self.db.fetch_one(query, (user_id,))

    async def list(self):
        query = """
        SELECT id, full_name, created_at
        FROM users
        ORDER BY full_name
        """
        return await self.db.fetch_all(query)

