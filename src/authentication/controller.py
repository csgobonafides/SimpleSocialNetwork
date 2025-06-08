import os
import jwt
from fastapi import Request
from datetime import timedelta, datetime, timezone

from core.exceptions import ForbiddenError, NotFoundError
from db.connector import DataBaseConnector


class Controller:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITM = os.getenv("ALGORITM")

    def __init__(self, db: DataBaseConnector):
        self.db = db

    async def registration(self, login: str, psw: str) -> bool:
        query = "SELECT * FROM accounts WHERE login = $1"
        check_user = await self.db.fetch(query, login)
        if check_user:
            raise ForbiddenError("A user with this login is already registered.")
        params = (login, psw)
        add_user = "INSERT INTO accounts (login, password) VALUES ($1, $2)"
        try:
            await self.db.execute(add_user, *params)
        except Exception as ex:
            raise ex
        else:
            return True

    async def authentication(self, login: str, psw: str) -> str:
        query = "SELECT id, login, password FROM accounts WHERE login = $1"
        result = await self.db.fetch(query, login)
        if not result:
            raise ForbiddenError("There is no user with this login.")
        user_id, user_login, user_psw = result[0]
        if psw != user_psw:
            raise ForbiddenError("Incorrect password.")
        return await self.create_token(user_id)

    async def create_token(self, user_id: int, time_of_life: int = 5) -> str:
        jwt_token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=time_of_life)
            },
            self.SECRET_KEY,
            alg=self.ALGORITM
        )
        return jwt_token

    async def check_token(self, request: Request) -> int | None:
        if request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            try:
                payload = jwt.decode(jwt_token, self.SECRET_KEY, algorithms=self.ALGORITM)
                if payload:
                    return int(payload.get("user_id"))
            except jwt.ExpiredSignatureError:
                raise ForbiddenError("The token has expired.")
            except jwt.InvalidTokenError:
                raise ForbiddenError("Invalid token.")
        else:
            raise NotFoundError("Token missing.")


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
