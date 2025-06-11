
import os
from datetime import timedelta, datetime, timezone
import jwt
from fastapi import Request

from core.exceptions import ForbiddenError
from db.connector import DataBaseConnector
from social_page.social_page_schemas import SocialPageRequest, SocialPageResponse
from core.exceptions import NotFoundError


class Controller:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITM = os.getenv("ALGORITM")

    def __init__(self, db: DataBaseConnector):
        self.db = db

    async def register(self, social_page: SocialPageRequest) -> None:
        check_user = """SELECT * FROM accounts WHERE login = $1;"""
        result_check = await self.db.fetch(check_user, social_page.login)
        if result_check:
            raise ForbiddenError("Such user is already registered.")
        add_user = """INSERT INTO accounts (login, password) VALUES ($1, $2) RETURNING id;"""
        params_user = (social_page.login, social_page.password)
        try:
            new_user_id = await self.db.fetchval(add_user, *params_user)
        except Exception as ex:
            raise ex

        create_page = """INSERT INTO social (id, first_name, last_name, data_of_birth, gender, interests, city)
        VALUES ($1, $2, $3, $4, $5, $6, $7);"""
        params_page = (
            new_user_id,
            social_page.first_name,
            social_page.last_name,
            social_page.data_of_birth,
            social_page.gender,
            social_page.interests,
            social_page.city
        )
        try:
            await self.db.execute(create_page, *params_page)
        except Exception as ex:
            raise ex

    async def login(self, login: str, password: str) -> dict:
        check_user = """SELECT * FROM accounts WHERE login = $1;"""
        result = await self.db.fetch(check_user, login)
        if not result:
            raise NotFoundError("User not found.")
        user_id, user_login, user_psw = result[0]
        if user_psw != password:
            raise ForbiddenError("Incorrect password.")

        return {"token": await self.create_token(user_id)}

    async def create_token(self, user_id: int, time_of_life: int = 5) -> str:
        jwt_token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=time_of_life)
            },
            self.SECRET_KEY,
            algorithm=self.ALGORITM
        )
        return jwt_token

    async def get_id(self, request: Request, user_id: int) -> SocialPageResponse | None:
        if not request.headers.get('authorization'):
            raise NotFoundError("Token missing.")
        jwt_token = request.headers.get('authorization')[7:]
        try:
            payload = jwt.decode(jwt_token, self.SECRET_KEY, algorithms=self.ALGORITM)
            if payload:
                query = """SELECT * FROM social WHERE id = $1;"""
                result = await self.db.fetch(query, user_id)
                record = result[0]
                print(record["id"])
                return SocialPageResponse(
                    page_id=record["id"],
                    first_name=record["first_name"],
                    last_name=record["last_name"],
                    data_of_birth=record["data_of_birth"],
                    gender=record["gender"],
                    interests=record["interests"],
                    city=record["city"]
                )
        except jwt.ExpiredSignatureError:
            raise ForbiddenError("The token has expired.")
        except jwt.InvalidTokenError:
            raise ForbiddenError("Invalid token.")
        except IndexError:
            raise NotFoundError("Record with this ID not found.")
        except Exception as ex:
            raise ex


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
