
from contextlib import asynccontextmanager
from fastapi import FastAPI

import authentication.controller as control_auth

from db.connector import DataBaseConnector
from core.settings import get_settings


app = FastAPI()

config = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database = DataBaseConnector(config.DB.db_url)
    await database.connect()
    await database.create_account_table()
    await database.create_social_table()
    control_auth.controller = control_auth.Controller(database)
    yield
    await database.disconnect()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
