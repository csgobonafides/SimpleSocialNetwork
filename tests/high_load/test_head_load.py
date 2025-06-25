from pathlib import Path
from datetime import date, datetime
from time import monotonic
import pytest

from db.connector import DataBaseConnector

path_people = Path(__file__).parent/"people.v2.csv"


@pytest.fixture
async def user_db(
        test_db: DataBaseConnector,
        file_people: Path,
        hash_psw: str
) -> list[tuple]:
    start_time = datetime.now()
    user_data = []
    psw = hash_psw
    with file_people.open("r", encoding="utf-8") as file:
        for i, line in enumerate(file):
            row = line.split(",")
            first_name, last_name = row[0].split(" ")
            data_of_birth = date.fromisoformat(row[1])
            user_data.append((str(i), psw, first_name, last_name, data_of_birth, "o", "programming", row[2]))
    await test_db.execute("INSERT INTO social VALUES ($1, $2, $3, $4, $5, $6, $7, $8);", *user_data)
    finish_time = datetime.now() - start_time
    print(finish_timeп)
    return user_data
