
from pydantic import BaseModel


class UserRequest(BaseModel):
    login: str
    password: str


class UserResponse(UserRequest):
    user_id: int
