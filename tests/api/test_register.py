
import pytest
from httpx import AsyncClient
from datetime import datetime

from db.connector import DataBaseConnector
from social_page.schemas import SocialPageRequest


@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_social")
async def test_register_201(xclient: AsyncClient, test_db: DataBaseConnector):
    payload = {
        "login": "ttest",
        "password": "ttest",
        "first_name": "ttest",
        "last_name": "ttest",
        "data_of_birth": datetime.now().date(),
        "gender": "O",
        "interests": "ttest",
        "city": "Ugansk"
    }
    response = await xclient.post("/register/", json=payload)
    assert response.status_code == 201, response.text
