
import os
import bcrypt

from core.exceptions import ForbiddenError
from db.connector import DataBaseConnector
from social_page.schemas import SocialPageRequest, SocialPageResponse, RegisterResponse, LoginResponse, SearchUser
from core.exceptions import NotFoundError
from jwt_token.jwt_token import create_token


class Controller:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITM = os.getenv("ALGORITM")

    def __init__(self, db: DataBaseConnector):
        self.db = db

    async def register(self, social_page: SocialPageRequest) -> RegisterResponse:
        check_user = """SELECT * FROM social WHERE login = $1;"""
        result_check = await self.db.fetch(check_user, social_page.login)
        if result_check:
            raise ForbiddenError("Such user is already registered.")

        hash_psw = bcrypt.hashpw(social_page.password.encode('utf-8'), bcrypt.gensalt())
        password = hash_psw.decode('utf-8')

        create_page = """INSERT INTO social (login, password, first_name, last_name, data_of_birth, gender, interests, city)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id;"""
        params_page = (
            social_page.login,
            password,
            social_page.first_name,
            social_page.last_name,
            social_page.data_of_birth,
            social_page.gender,
            social_page.interests,
            social_page.city
        )
        try:
            user_id = await self.db.fetchval(create_page, *params_page)
            return RegisterResponse(id=user_id)
        except Exception as ex:
            raise ex

    async def login(self, login: str, password: str) -> LoginResponse:
        check_user = """SELECT * FROM social WHERE login = $1;"""
        result = await self.db.fetch(check_user, login)
        if not result:
            raise NotFoundError("User not found.")
        user_id = result[0].get("id")
        user_psw = result[0].get("password")
        if not bcrypt.checkpw(password.encode('utf-8'), user_psw.encode('utf-8')):
            raise ForbiddenError("Incorrect password.")
        return LoginResponse(token=create_token(user_id))

    async def get_id(self, user_id: int) -> SocialPageResponse | None:
        try:
            query = """SELECT * FROM social WHERE id = $1;"""
            result = await self.db.fetch(query, user_id)
            if not result:
                raise NotFoundError("No user with this id found.")
            record = result[0]
            return SocialPageResponse(
                id=record["id"],
                first_name=record["first_name"],
                last_name=record["last_name"],
                data_of_birth=record["data_of_birth"],
                gender=record["gender"],
                interests=record["interests"],
                city=record["city"]
            )
        except Exception as ex:
            raise ex


    async def user_search(self, params: SearchUser) -> list[SocialPageResponse]:
        users = await self.db.fetch(
            """SELECT * FROM social WHERE first_name LIKE $1 AND last_name LIKE $2 ORDER BY id""",
            params.first_name, params.last_name,
        )
        return [SocialPageResponse(**user) for user in users]


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
