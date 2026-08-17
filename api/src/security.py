import secrets

from fastapi import Header, HTTPException, status

from src.config import settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if settings.api_key and (
        x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key)
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API key")
