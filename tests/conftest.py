
import pytest
import pytest_asyncio
from httpx import AsyncClient

from db.connector import DataBaseConnector
from core.settings import get_settings, Settings
import social_page.controller as social_modul
from main import app


pytest_plugins = [
    "fixtures.test_db",
    "fixtures.prepare_social"
]


@pytest.fixture(scope="session")
def settings() -> str:
    return get_settings()


@pytest_asyncio.fixture(autouse=True)
async def social_controller(test_db: DataBaseConnector) -> social_modul.Controller:
    social_modul.controller = social_modul.Controller(test_db)
    yield social_modul.controller


@pytest_asyncio.fixture
async def xclient() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8010") as cli:
        yield cli
