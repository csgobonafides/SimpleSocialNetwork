
from core.exceptions import ForbiddenError
from db.connector import DataBaseConnector
from social_page.social_page_schemas import SocialPageRequest, SocialPageResponse
from core.exceptions import NotFoundError


class Controller:

    def __init__(self, db: DataBaseConnector):
        self.db = db

    async def create_social_page(self,user_id: int, page: SocialPageRequest) -> SocialPageResponse:
        query = f"""INSERT INTO social (id, first_name, last_name, data_of_birth, gender, interests, city)
        VALUES (
        {user_id}, 
        {page.first_name}, 
        {page.last_name}, 
        {page.data_of_birth}, 
        {page.gender}, 
        {page.interests}, 
        {page.city}
        )"""
        try:
            await self.db.execute(query)
        except Exception as ex:
            raise ex
        else:
            return SocialPageResponse(
                page_id=user_id,
                first_name=page.first_namem,
                last_name=page.last_name,
                data_of_birth=page.data_of_birth,
                gender=page.gender,
                interests=page.interests,
                city=page.city
            )

    async def get_social_page_id(self, user_id: int) -> SocialPageResponse:
        query = """SELECT * FROM social WHERE id = $1;"""
        result = await self.db.fetch(query, user_id)
        return SocialPageResponse(
            page_id=result.get("page_id"),
            first_name=result.get("first_name"),
            last_name=result.get("last_name"),
            data_of_birth=result.get("data_of_birth"),
            gender=result.get("gender"),
            interests=result.get("interests"),
            city=result.get("city")
        )

    async def get_social_page_all(self, page: int = 1, page_size: int = 5) -> list[SocialPageResponse]:
        offset = (page - 1) * page_size
        params = (page_size, offset)
        query = """SELECT * FROM social LIMIT $1 OFFSET $2;"""
        results = await self.db.fetch(query, *params)
        if results:
            return [
                SocialPageResponse(
                    page_id=result.get("page_id"),
                    first_name=result.get("first_name"),
                    last_name=result.get("last_name"),
                    data_of_birth=result.get("data_of_birth"),
                    gender=result.get("gender"),
                    interests=result.get("interests"),
                    city=result.get("city")
                )
                for result in results
            ]
        else:
            raise NotFoundError


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError("Controller in None.")
    return controller
