
import uuid
from pathlib import Path
import pytest
import asyncpg

from core.settings import Settings, DatabaseConfig
from db.connector import DataBaseConnector

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent / "src"


@pytest.fixture(scope="session")
def database_name() -> str:
    return f"{uuid.uuid4().hex}.pytest"


@pytest.fixture(scope="session")
def database(settings: Settings) -> DatabaseConfig:
    return settings.DB


@pytest.fixture(scope="session")
async def prepare_test_database(database_name: str, database: DatabaseConfig) -> None:
    admin_conn = await asyncpg.connect(
        user=database['USERNAME'],
        password=database['PASSWORD'],
        host=database['HOST'],
        port=database['PORT'],
        database=database['NAME']
    )
    await admin_conn.execute(f'CREATE DATABASE "{database_name}"')
    await admin_conn.close()

    test_dns = (f"postgresql://{database['USERNAME']}:{database['PASSWORD']}@"
                f"{database['HOST']}:{database['PORT']}/{database_name}")
    test_conn = await asyncpg.connect(test_dns)
    try:
        await test_conn.execute("""
                CREATE TABLE IF NOT EXISTS social (
                    id SERIAL PRIMARY KEY,
                    login VARCHAR(50) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    data_of_birth DATE NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    interests VARCHAR(100) NOT NULL,
                    city VARCHAR(50) NOT NULL
                );
                """)
        yield test_dns
    finally:
        await test_conn.close()
        admin_conn = await asyncpg.connect(
            user=database["USERNAME"],
            password=database["PASSWORD"],
            host=database["HOST"],
            port=database["PORT"],
            database=database['NAME']
        )
        await admin_conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database_name}' AND pid <> pg_backend_pid();
                """)
        await admin_conn.execute(f'DROP DATABASE "{database_name}"')
        await admin_conn.close()


@pytest.fixture
async def test_db(prepare_test_database: str, database: DatabaseConfig, database_name: str) -> DataBaseConnector:
    conn = await asyncpg.connect(prepare_test_database)
    try:
        tr = conn.transaction()
        await tr.start()
        try:
            yield conn
        finally:
            await tr.rollback()
    finally:
        await conn.close()
