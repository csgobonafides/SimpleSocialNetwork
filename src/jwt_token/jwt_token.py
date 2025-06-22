from datetime import datetime, timezone, timedelta

import jwt
import os
from fastapi import Request

from core.exceptions import ForbiddenError


_secret_key = os.getenv("SECRET_KEY")
_algoritm = os.getenv("ALGORITM")


def check_token(request: Request) -> int:

    if not request.headers.get('authorization'):
        raise ForbiddenError("Token missing.")
    jwt_token = request.headers.get('authorization')[7:]
    try:
        payload = jwt.decode(jwt_token, _secret_key, algorithms=_algoritm)
        if not payload:
            raise ForbiddenError
        return payload
    except jwt.ExpiredSignatureError:
        raise ForbiddenError("The token has expired.")
    except jwt.InvalidTokenError:
        raise ForbiddenError("Invalid token.")
    except Exception as ex:
        raise ForbiddenError(str(ex))


def create_token(user_id: int, time_of_life: int = 5) -> str:
    jwt_token = jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=time_of_life)
        },
        _secret_key,
        algorithm=_algoritm
    )
    return jwt_token
