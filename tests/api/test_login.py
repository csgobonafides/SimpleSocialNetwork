
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_login_200(xclient: AsyncClient, hash_psw: str):
    payload = {"login": "test1", "password": "tests1"}
    response = await xclient.post("/social_page/login", json=payload)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert isinstance(token, str) and len(token) == 121


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_login_404(xclient: AsyncClient, hash_psw: str):
    payload = {"login": "wwww", "password": "tests1"}
    response = await xclient.post("/social_page/login", json=payload)
    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'User not found.'}


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_login_403(xclient: AsyncClient, hash_psw: str):
    payload = {"login": "test1", "password": "wwww"}
    response = await xclient.post("/social_page/login", json=payload)
    assert response.status_code == 403, response.text
    assert response.json() == {'detail': 'Incorrect password.'}
