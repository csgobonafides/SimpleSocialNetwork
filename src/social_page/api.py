
from fastapi import APIRouter, Depends, Request, Query

from social_page.controller import get_controller
from social_page.social_page_schemas import SocialPageRequest, SocialPageResponse, User


router = APIRouter()


@router.post("/login")
async def login(user: User, controller = Depends(get_controller)) -> dict:
    return await controller.login(user.login, user.password)


@router.get("/user/{user_id}")
async def get_id(
        user_id: int,
        request: Request,
        controller = Depends(get_controller)
) -> SocialPageResponse:
    return await controller.get_id(request, user_id)


@router.post("/user/register")
async def register(
        social_page: SocialPageRequest,
        controller = Depends(get_controller)
) -> SocialPageResponse:
    return await controller.register(social_page)
