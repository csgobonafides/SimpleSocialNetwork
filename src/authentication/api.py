
from fastapi import APIRouter, status, Depends, Request

from authentication.user_schemas import UserRequest
from authentication.controller import get_controller


router = APIRouter()


@router.post("/registration", response_model=bool, status_code=status.HTTP_201_CREATED)
async def registration(
        user: UserRequest,
        controller = Depends(get_controller)
) -> bool:
    return await controller.registration(user.login, user.password)


@router.post("/authentication", response_model=str, status_code=status.HTTP_200_OK)
async def authentication(
        user: UserRequest,
        controller = Depends(get_controller)
) -> str:
    return await controller.authentication(user.login, user.password)

@router.post("/examination", response_model=int, status_code=status.HTTP_200_OK)
async def examination(
        request: Request,
        controller = Depends(get_controller)
) -> int:
    return await controller.check_token(request)
