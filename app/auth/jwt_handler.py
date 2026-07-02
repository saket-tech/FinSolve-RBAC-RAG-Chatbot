"""JWT token creation and validation."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.auth.rbac import Role
from app.config.settings import get_settings


def create_access_token(username: str, role: Role) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": username,
        "role": role.value,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username = payload.get("sub")
        role_value = payload.get("role")
        if not username or not role_value:
            return None
        return {"username": username, "role": Role(role_value)}
    except (JWTError, ValueError):
        return None
