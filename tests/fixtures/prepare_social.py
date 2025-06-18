import bcrypt
import pytest
import pytest_asyncio
from datetime import datetime

from db.connector import DataBaseConnector
from social_page.schemas import SocialPageRequest



@pytest.fixture
def hash_psw() -> str:
    hash_psw = bcrypt.hashpw("tests1".encode('utf-8'), bcrypt.gensalt())
    password = hash_psw.decode('utf-8')
    return str(password)


@pytest.fixture
def social(hash_psw: str) -> SocialPageRequest:
    return SocialPageRequest(
        login="test1",
        password=hash_psw,
        first_name="tests",
        last_name="tests",
        data_of_birth=datetime.now(),
        gender="O",
        interests="tests",
        city="ugansk"
    )


@pytest_asyncio.fixture
async def prepare_social(test_db: DataBaseConnector, social: SocialPageRequest) -> None:
    await test_db.execute(
        """
        INSERT INTO social (
            login, password, first_name, last_name, 
            data_of_birth, gender, interests, city
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        social.login,
        social.password,
        social.first_name,
        social.last_name,
        social.data_of_birth,
        social.gender,
        social.interests,
        social.city,
    )
