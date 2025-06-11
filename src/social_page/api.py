
from fastapi import APIRouter, Depends, Request, status

from social_page.controller import get_controller
from social_page.social_page_schemas import SocialPageRequest, SocialPageResponse, User


router = APIRouter()


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(user: User, controller = Depends(get_controller)) -> dict:
    return await controller.login(user.login, user.password)


@router.get("/user/{user_id}", response_model=SocialPageResponse, status_code=status.HTTP_200_OK)
async def get_id(
        user_id: int,
        request: Request,
        controller = Depends(get_controller)
) -> SocialPageResponse:
    return await controller.get_id(request, user_id)


@router.post("/user/register", response_model=None, status_code=status.HTTP_201_CREATED)
async def register(
        social_page: SocialPageRequest,
        controller = Depends(get_controller)
) -> None:
    return await controller.register(social_page)
