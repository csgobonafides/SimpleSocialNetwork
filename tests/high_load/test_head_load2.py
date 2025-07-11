import asyncio
from pathlib import Path
from datetime import date, datetime
from random import randint
from time import monotonic
from functools import wraps
from typing import Callable, Any

import pytest_asyncio
from httpx import AsyncClient

import bcrypt
import pytest

from db.connector import DataBaseConnector


REQUEST_COUNT = 5000


def statistic_decor(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = monotonic()
        request_count = 0
        all_latency = []

        async def stat_callback(latency: float):
            nonlocal request_count, all_latency
            request_count += 1
            all_latency.append(latency)

        kwargs['_stats_callback'] = stat_callback

        try:
            result = await func(*args, **kwargs)
        finally:
            total_time = monotonic() - start_time
            rps = round(request_count / total_time, 2)
            min_latency = min(all_latency)
            max_latency = max(all_latency)
            avg_latency = round(sum(all_latency) / len(all_latency), 2)

            print(f"Request count: {request_count}")
            print(f"Total time: {round(total_time, 1)}s")
            print(f"Requests per second: {rps}")
            print(f"Min latency: {min_latency}ms")
            print(f"Max latency: {max_latency}ms")
            print(f"Average latency: {avg_latency}ms")
        return result
    return wrapper


@pytest.fixture
def file_people() -> Path:
    current_dir = Path(__file__).parent
    return current_dir / "people.csv"


@pytest_asyncio.fixture
async def user_db(
        test_db: DataBaseConnector,
        file_people: Path,
        hash_psw: str
) -> list[tuple]:
    start_time = datetime.now()
    user_data = []
    psw = bcrypt.hashpw("top_secret_password".encode(), bcrypt.gensalt()).decode()
    with file_people.open("r", encoding='utf-8') as file:
        for i, line in enumerate(file):
            row = line.split(",")
            first_name, last_name = row[0].split(" ")
            birthdate = date.fromisoformat(row[1])
            user_data.append(
                (str(i), psw, first_name, last_name, birthdate, "-", "high load projects", row[2]),
            )
        await test_db.executemany("""INSERT INTO social 
        (login, password, first_name, last_name, data_of_birth, gender, interests, city) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""", user_data)
    print(f"Generated users in {datetime.now() - start_time}")
    return user_data


@pytest.mark.asyncio
@pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
@statistic_decor
async def test_not_index(
        xclient: AsyncClient,
        test_db: DataBaseConnector,
        user_db: list[tuple],
        jwt_token: str,
        thread_count: int,
        _stats_callback: Callable[[float], None] = None
):
    count = await test_db.fetchval("SELECT COUNT(*) FROM social;")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    request_per_thread = REQUEST_COUNT // thread_count

    async def make_request():
        for _ in range(request_per_thread):
            start_time = monotonic()
            i = randint(0, count - 1)
            params = {"first_name": user_db[i][2][:3], "last_name": user_db[i][3][:3]}
            await xclient.get("/social_page/users/search", params=params, headers=headers)
            latency = round(1000.0 * (monotonic() - start_time), 3)
            if _stats_callback:
                await _stats_callback(latency)

    await asyncio.gather(*[asyncio.create_task(make_request()) for _ in range(thread_count)])


@pytest.mark.asyncio
@pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
@statistic_decor
async def test_with_index(
        xclient: AsyncClient,
        test_db: DataBaseConnector,
        user_db: list[tuple],
        jwt_token: str,
        thread_count: int,
        _stats_callback: Callable[[float], None] = None
):
    count = await test_db.fetchval("SELECT COUNT(*) FROM social;")
    await test_db.execute("CREATE INDEX social_name_id_idx ON social(first_name, last_name, id);")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    request_per_thread = REQUEST_COUNT // thread_count

    async def make_request():
        for _ in range(request_per_thread):
            start_time = monotonic()
            i = randint(0, count - 1)
            params = {"first_name": user_db[i][2][:3], "last_name": user_db[i][3][:3]}
            await xclient.get("/social_page/users/search", params=params, headers=headers)
            latency = round(1000.0 * (monotonic() - start_time), 3)
            if _stats_callback:
                await _stats_callback(latency)

    await asyncio.gather(*[asyncio.create_task(make_request()) for _ in range(thread_count)])


@pytest.mark.asyncio
async def test_explain(test_db: DataBaseConnector, user_db: list[tuple]):
    count = await test_db.fetchval("SELECT COUNT(*) FROM social;")
    await test_db.execute("CREATE INDEX social_name_id_idx ON social(first_name, last_name, id);")
    i = randint(0, count - 1)
    first_name, last_name = user_db[i][2][:3], user_db[i][3][:3]
    result = await test_db.fetch("EXPLAIN ANALYZE SELECT * FROM social WHERE first_name ILIKE $1 AND last_name ILIKE $2 ORDER BY id",
                                 f"{first_name}%",
                                 f"{last_name}%",
                                 )
    print("\n")
    for i in result:
        print(next(i.values()))
