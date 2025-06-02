import os

from src.core.exceptions import ForbiddenError


class Controller:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITM = os.getenv("ALGORITM")

    def __init__(self, db):
        self.db = db

    async def registration(self):
        pass

    async def authentication(self):
        pass

    async def creat_token(self):
        pass

    async def check_token(self):
        pass


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
