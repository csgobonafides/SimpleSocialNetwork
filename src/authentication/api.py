
from fastapi import APIRouter

router = APIRouter()


@router.post("/registration")
async def registration():
    pass


@router.post("/authentication")
async def authentication():
    pass
