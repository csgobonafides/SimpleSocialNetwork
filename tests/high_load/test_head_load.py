import asyncio
from pathlib import Path
from datetime import date, datetime
from random import randint
from time import monotonic

import pytest_asyncio
from httpx import AsyncClient
from dataclasses import dataclass, field

import bcrypt
import pytest

from db.connector import DataBaseConnector


REQUEST_COUNT = 5000


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


@dataclass
class Statistics:
    count: int
    start_time: datetime
    end_time: datetime = field(init=False)
    latencies: list[float] = field(default_factory=list)

    def show(self) -> None:
        total_time = round((self.end_time - self.start_time).total_seconds(), 2)
        rps = round(self.count / total_time, 2)
        min_latency = min(self.latencies)
        max_latency = max(self.latencies)
        avg_latency = round(sum(self.latencies) / len(self.latencies), 2)

        print(f"Request count: {self.count}")
        print(f"Total time: {total_time}s")
        print(f"Requests per second: {rps}")
        print(f"Min latency: {min_latency}ms")
        print(f"Max latency: {max_latency}ms")
        print(f"Average latency: {avg_latency}ms")


@pytest_asyncio.fixture
async def timeit_request(
        xclient: AsyncClient,
        test_db: DataBaseConnector,
        user_db: list[tuple],
        jwt_token: str
) -> callable:
    count = await test_db.fetchval("SELECT COUNT(*) FROM social")
    headers = {"Authorization": f"Bearer {jwt_token}"}

    async def inner(request_per_thread: int, stat: Statistics) -> None:
        for _ in range(request_per_thread):
            start_time = monotonic()
            i = randint(0, count - 1)
            params = {"first_name": user_db[i][1][:3], "last_name": user_db[i][2][:3]}
            await xclient.get("/user/search", params=params, headers=headers)
            latency = round(1000.0 * (monotonic() - start_time), 3)
            stat.latencies.append(latency)

    return inner


@pytest.mark.asyncio
@pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
async def test_high_load_with_index(test_db: DataBaseConnector, timeit_request: callable, thread_count: int) -> None:
    await test_db.execute("CREATE INDEX social_name_id_idx ON social(first_name, last_name, id);")
    request_per_thread = REQUEST_COUNT // thread_count
    stat = Statistics(REQUEST_COUNT, datetime.now())

    await asyncio.gather(
        *[asyncio.create_task(timeit_request(request_per_thread, stat)) for _ in range(thread_count)],
    )
    stat.end_time = datetime.now()
    stat.show()


# @pytest.mark.asyncio
# @pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
# async def test_high_load_with_index(test_db: DataBaseConnector, timeit_request: callable, thread_count: int) -> None:
#     await test_db.execute("CREATE INDEX social_name_id_idx ON social(first_name, last_name, id);")
#     request_per_thread = REQUEST_COUNT // thread_count
#     stat = Statistics(REQUEST_COUNT, datetime.now())
#
#     await asyncio.gather(
#         *[asyncio.create_task(timeit_request(request_per_thread, stat) for _ in range(thread_count))]
#     )
#     stat.end_time = datetime.now()
#     stat.show()
#
#
# @pytest.mark.asyncio
# async def test_high_load_with_index_explain(test_db: DataBaseConnector, timeit_request: callable, user_db: list[tuple]) -> None:
#     await test_db.execute("CREATE INDEX social_name_id_idx ON social(first_name, last_name, id);")
#     count = await test_db.fetchval("SELECT COUNT(*) FROM social")
#     i = randint(0, count - 1)
#     first_name, last_name = user_db[i][1][:3], user_db[i][2][:3]
#     result = await test_db.fetch(
#         "EXPLAIN ANALYZE SELECT * FROM social WHERE first_name LIKE $1 AND last_name LIKE $2 ORDER BY id",
#         f"{first_name}%",
#         f"{last_name}%",
#     )
#     print("\n")
#     for row in result:
#         print(next(row.values()))
