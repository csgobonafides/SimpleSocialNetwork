
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_register_201(xclient: AsyncClient):
    payload = {
        "login": "ttest",
        "password": "ttest",
        "first_name": "ttest",
        "last_name": "ttest",
        "data_of_birth": str(datetime.now().date()),
        "gender": "O",
        "interests": "ttest",
        "city": "Ugansk"
    }
    response = await xclient.post("/social_page/users/register", json=payload)
    assert response.status_code == 201, response.text


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_register_403(xclient: AsyncClient):
    payload = {
        "login": "test1",
        "password": "ttest",
        "first_name": "ttest",
        "last_name": "ttest",
        "data_of_birth": str(datetime.now().date()),
        "gender": "O",
        "interests": "ttest",
        "city": "Ugansk"
    }
    response = await xclient.post("/social_page/users/register", json=payload)
    assert response.status_code == 403, response.text
    assert response.json() == {"detail": "Such user is already registered."}


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_register_422(xclient: AsyncClient):
    payload = {
        "login": "Vika",
        "password": 123,
        "first_name": "ttest",
        "last_name": "ttest",
        "data_of_birth": str(datetime.now().date()),
        "gender": "O",
        "interests": "ttest",
        "city": "Ugansk"
    }
    response = await xclient.post("/social_page/users/register", json=payload)
    assert response.status_code == 422, response.text
    assert response.json() == {"detail": [
        {"type": "string_type",
         "loc": ["body","password"],
         "msg": "Input should be a valid string",
         "input": 123}
    ]}
