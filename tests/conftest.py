
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from db.connector import DataBaseConnector
from core.settings import get_settings
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
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(base_url="http://127.0.0.1:8010", transport=transport) as cli:
        yield cli
