
from fastapi import APIRouter, Depends, status

from social_page.controller import get_controller
from social_page.schemas import SocialPageRequest, SocialPageResponse, User, LoginResponse, RegisterResponse, SearchUser


router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
        user: User,
        controller = Depends(get_controller)
) -> LoginResponse:
    return await controller.login(user.login, user.password)


@router.get("/users/{user_id}", response_model=SocialPageResponse, status_code=status.HTTP_200_OK)
async def get_id(
        user_id: int,
        controller = Depends(get_controller)
) -> SocialPageResponse:
    return await controller.get_id(user_id)


@router.post("/users/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
        social_page: SocialPageRequest,
        controller = Depends(get_controller)
) -> None:
    return await controller.register(social_page)


@router.get("/users/search", response_model=list[SocialPageResponse], status_code=status.HTTP_200_OK)
async def user_search(
        params: SearchUser,
        controller = Depends(get_controller)
) -> list[SocialPageResponse]:
    return await controller.user_search(params=params)
