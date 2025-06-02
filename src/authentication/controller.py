import os

from core.exceptions import ForbiddenError
from db.connector import DataBaseConnector


class Controller:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITM = os.getenv("ALGORITM")

    def __init__(self, db: DataBaseConnector):
        self.db = db

    async def registration(self, login: str, psw: str) -> bool:
        query = f"SELECT * FROM accounts WHERE login = {login}"
        check_user = await self.db.fetch(query)
        if check_user:
            raise ForbiddenError("A user with this login is already registered.")
        add_user = f"INSERT INTO accounts (login, password) VALUES ({login}, {psw})"
        try:
            await self.db.execute(add_user)
        except Exception as ex:
            raise ex
        else:
            return True

    async def authentication(self):
        pass

    async def create_token(self):
        pass

    async def check_token(self):
        pass

    async def check_user(self, login: str, psw: str):
        pass


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
