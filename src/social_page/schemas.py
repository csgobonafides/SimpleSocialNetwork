
from pydantic import BaseModel, Field
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
    page_id: int = Field(alias="id")
    first_name: str
    last_name: str
    data_of_birth: date
    gender: str
    interests: str
    city: str


class User(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    token: str


class RegisterResponse(BaseModel):
    user_id: int = Field(alias="id")


class SearchUser(BaseModel):
    first_name: str
    last_name: str
