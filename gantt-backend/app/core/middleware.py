import fastapi
import jose

from app.core import security

EXEMPT_PATHS = {
    "/docs",
    "/openapi.json",
    "/api/login",
    "/api/register",
    "/api/check-email",
    "/api/refresh",
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
    except jose.exceptions.ExpiredSignatureError:
        refresh_token = request.headers.get("X-Refresh-Token")

        if not refresh_token:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"detail": "Access токен истек, требуется обновление"})

        try:
            new_access_token = security.refresh_access_token(refresh_token)
            payload = security.decode_access_token(new_access_token)
            request.state.new_access_token = new_access_token
        except ValueError as e:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"detail": f"Refresh токен истек или невалиден: {str(e)}"})
    except jose.JWTError:
        return fastapi.responses.JSONResponse(status_code=401,
                                              content={"detail": "Недействительный или просроченный токен"})

    user_id = payload.get("sub")

    if not user_id:
        return fastapi.responses.JSONResponse(status_code=401, content={"detail": "Некорректный токен"})

    request.state.user_id = int(user_id)

    response = await call_next(request)

    if hasattr(request.state, "new_access_token"):
        response.headers["X-New-Access-Token"] = request.state.new_access_token

    return response
