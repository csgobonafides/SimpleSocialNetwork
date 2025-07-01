
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_get_id_200(xclient: AsyncClient, jwt_token: str):
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    response = await xclient.get("/social_page/users/1", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": 1,
        "first_name": "tests",
        "last_name": "tests",
        "data_of_birth": "1992-09-23",
        "gender": "O",
        "interests": "tests",
        "city": "ugansk"
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_get_id_403(xclient: AsyncClient):
    response = await xclient.get("/social_page/users/1")
    assert response.status_code == 403, response.text
    assert response.json() == {'detail': '403: Token missing.'}


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_get_id_invalid_token_error_403(xclient: AsyncClient, jwt_token: str):
    headers = {
        "Authorization": f"Bearer {jwt_token+'a'}"
    }
    response = await xclient.get("/social_page/users/1", headers=headers)
    assert response.status_code == 403, response.text
    assert response.json() == {'detail': '403: Invalid token.'}


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_get_id_expired_signature_error_403(xclient: AsyncClient):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0LCJleHAiOjE3NTA0MzQzOTh9.Ae25pmo9lKKOytOi-sL_Sj4TCgtgVu8FZTGj-UpreC4"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = await xclient.get("/social_page/users/1", headers=headers)
    assert response.status_code == 403, response.text
    assert response.json() == {'detail': '403: The token has expired.'}


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_get_id_404(xclient: AsyncClient, jwt_token: str):
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    response = await xclient.get("/social_page/users/22", headers=headers)
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "No user with this id found."}
