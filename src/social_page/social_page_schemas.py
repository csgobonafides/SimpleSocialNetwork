
from pydantic import BaseModel
from datetime import date


class SocialPageRequest(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str
    data_of_birth: date
    gender: str
    interests: str
    city: str


class SocialPageResponse(BaseModel):
    page_id: int
    first_name: str
    last_name: str
    data_of_birth: date
    gender: str
    interests: str
    city: str


class User(BaseModel):
    login: str
    password: str
