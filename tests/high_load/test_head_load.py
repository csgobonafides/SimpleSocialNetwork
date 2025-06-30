from pathlib import Path
from datetime import date, datetime
import pytest
import csv

from db.connector import DataBaseConnector


@pytest.fixture
def file_people() -> Path:
    current_dir = Path(__file__).parent
    return current_dir / "people.v2.csv"


@pytest.fixture
async def user_db(
        db: DataBaseConnector,
        file_people: Path,
        hash_psw: str
) -> list[tuple]:
    start_time = datetime.now()
    user_data = []
    try:
        with file_people.open("r", encoding="cp1251") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if len(row) < 3:
                    continue
                first_name, last_name = row[0].split(" ", maxsplit=1)
                data_of_birth = date.fromisoformat(row[1].strip())
                user_data.append((
                    str(i),
                    hash_psw,
                    first_name,
                    last_name,
                    data_of_birth,
                    "o",
                    "programming",
                    row[2].strip()
                ))
                await db.executemany(
                    """INSERT INTO social (login, password, first_name, last_name, data_of_birth, gender, interests, city) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8);""",
                    user_data
                )
        print(f"Generated users in {datetime.now() - start_time}")
        return user_data
    except Exception as ex:
        raise ex
