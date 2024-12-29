from repositories.user import UserRepository, User

class UserService():
    def __init__(self, user_repository = UserRepository()):
        self.user_repository = user_repository

    async def get_user(self, pocket_access_token: str) -> User:
        return await self.user_repository.get_user(pocket_access_token)

    async def save_user(self, username: str, pocket_access_token: str) -> User:
        user = User(username=username, pocket_access_token=pocket_access_token)
        return await self.user_repository.save_user(user)
