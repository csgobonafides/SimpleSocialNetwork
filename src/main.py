
from contextlib import asynccontextmanager
from fastapi import FastAPI

import social_page.controller as control_page

from db.connector import DataBaseConnector
from core.settings import get_settings
from social_page.api import router as social_router


config = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database = DataBaseConnector(config.DB.db_url)
    await database.connect()
    await database.create_account_table()
    await database.create_social_table()
    control_page.controller = control_page.Controller(database)
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(social_router, tags=["social_page"], prefix="/social_page")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
