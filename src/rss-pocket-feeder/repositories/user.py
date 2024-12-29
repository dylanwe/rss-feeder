from dataclasses import dataclass
from db import get_db

@dataclass
class User:
    pocket_access_token: str
    username: str

class UserRepository:
    def __init__(self, db = next(get_db())):
        self.db = db

    async def get_user(self, pocket_access_token: str) -> User:
        cur = self.db.cursor()
        cur.execute("SELECT pocket_access_token, username FROM users WHERE pocket_access_token = ?", (pocket_access_token,))
        user = cur.fetchone()
        cur.close()
        return User(pocket_access_token=user[0], username=user[1])

    async def save_user(self, user: User) -> User:
        cur = self.db.cursor()
        cur.execute("INSERT INTO users (pocket_access_token, username) VALUES (?, ?)", (user.pocket_access_token, user.username))
        self.db.commit()
        cur.close()
        return user

