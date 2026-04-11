from db.user_repo import user_repo


class UserService:
    def __init__(self, repo):
        self.repo = repo

    async def get_user(self, user_id: str):
        return await self.repo.get(user_id)

    async def list_users(self):
        return await self.repo.list()


user_service = UserService(user_repo)
