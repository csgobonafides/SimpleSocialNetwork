
from fastapi import APIRouter, Depends, Request, Query

from authentication.controller import get_controller as control_auth
from social_page.controller import get_controller as control_page

from social_page.social_page_schemas import SocialPageRequest, SocialPageResponse
from core.exceptions import ForbiddenError


router = APIRouter()


@router.get("/{user_id}")
async def get_social_page_id(
        user_id: int,
        request: Request,
        controll_auth = Depends(control_auth),
        controll_page = Depends(control_page)
) -> SocialPageResponse:
    user = await controll_auth.check_token(request)
    if isinstance(user, int):
        return await controll_page.get_social_page_id(user_id)
    raise ForbiddenError


@router.get("/")
async def get_all_social_page(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(5, ge=1),
        controll_auth = Depends(control_auth),
        controll_page = Depends(control_page),
) -> list[SocialPageResponse]:
    user = await controll_auth.check_token(request)
    if isinstance(user, int):
        return await controll_page.get_social_page_all(page, page_size)
    raise ForbiddenError


@router.post("/")
async def create_social_page(
        page: SocialPageRequest,
        request: Request,
        controll_auth = Depends(control_auth),
        controll_page = Depends(control_page)
) -> SocialPageResponse:
    user_id = await controll_auth.check_token(request)
    if isinstance(user_id, int):
        return await controll_page.create_social_page(user_id, page)
    raise ForbiddenError
