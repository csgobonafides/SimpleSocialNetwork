
from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

import social_page.controller as control_page

from db.connector import DataBaseConnector
from core.settings import get_settings
from social_page.router import router as social_router
from jwt_token.jwt_token import check_token
from core.exceptions import NotFoundError, ForbiddenError


config = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database = DataBaseConnector(config.DB.db_url)
    await database.connect()
    await database.create_social_table()
    control_page.controller = control_page.Controller(database)
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(social_router, tags=["social_page"], prefix="/social_page")


@app.middleware("http")
async def check_jwt_middleware(request: Request, call_next):
    excluded_paths = [
        "/social_page/login",
        "/social_page/users/register",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico"
    ]
    if (
            request.url.path.rstrip("/") in excluded_paths
            or request.url.path.startswith("/docs/")
            or request.url.path.startswith("/static/")
    ):
        return await call_next(request)
    try:
        check_token(request)
        return await call_next(request)
    except jwt.ExpiredSignatureError as ex:
        return JSONResponse(status_code=403, content={"detail": str(ex)})
    except jwt.InvalidTokenError as ex:
        return JSONResponse(status_code=403, content={"detail": str(ex)})
    except NotFoundError as ex:
        return JSONResponse(status_code=404, content={"detail": str(ex)})
    except ForbiddenError as ex:
        return JSONResponse(status_code=403, content={"detail": str(ex)})
    except Exception as ex:
        return JSONResponse(status_code=500, content={"detail": str(ex)})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
