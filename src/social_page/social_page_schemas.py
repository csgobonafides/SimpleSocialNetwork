
from pydantic import BaseModel
from datetime import date


class SocialPageRequest(BaseModel):
    first_name: str
    last_name: str
    data_of_birth: date
    gender: str
    interests: str
    city: str


class SocialPageResponse(SocialPageRequest):
    page_id: int
