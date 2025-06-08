
from contextlib import asynccontextmanager
from fastapi import FastAPI

import authentication.controller as control_auth
import social_page.controller as control_page

from db.connector import DataBaseConnector
from core.settings import get_settings

from authentication.api import router as auth_router
from social_page.api import router as social_router


app = FastAPI()
app.include_router(auth_router, tags=["authentication"], prefix="/authentication")
app.include_router(social_router, tags=["social_page"], prefix="/social_page")

config = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database = DataBaseConnector(config.DB.db_url)
    await database.connect()
    await database.create_account_table()
    await database.create_social_table()
    control_auth.controller = control_auth.Controller(database)
    control_page.controller = control_page.Controller(database)
    yield
    await database.disconnect()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
