import fastapi
import jose
from app.core import security

EXEMPT_PATHS = {
    "/api/login",
    "/api/register",
    "/api/check-email",
    "/api/taskStatuses",
    "/api/priorities",
    "/api/connectionTypes",
}

async def auth_middleware(request: fastapi.Request, call_next):
    path = request.url.path

    if any(path.startswith(p) for p in EXEMPT_PATHS):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return fastapi.responses.JSONResponse(status_code=401, content={"detail": "Отсутствует токен авторизации"})

    token = auth_header.split(" ", 1)[1]

    try:
        payload = security.decode_access_token(token)
    except jose.JWTError:
        return fastapi.responses.JSONResponse(status_code=401, content={"detail": "Недействительный или просроченный токен"})

    user_id = payload.get("sub")

    if not user_id:
        return fastapi.responses.JSONResponse(status_code=401, content={"detail": "Некорректный токен"})

    request.state.user_id = int(user_id)

    return await call_next(request)