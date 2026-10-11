from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.email import is_allowed_email
from app.config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)
_AUTH_USER_PATH = "/auth/v1/user"


@dataclass(frozen=True, slots=True)
class CurrentUser:
    user_id: UUID
    email: str


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def fetch_auth_user(
    token: str,
    settings: Settings,
    http_client: httpx.AsyncClient,
) -> CurrentUser | None:
    response = await http_client.get(
        f"{settings.supabase_url.rstrip('/')}{_AUTH_USER_PATH}",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": settings.supabase_anon_key,
        },
    )
    if response.status_code >= 500:
        response.raise_for_status()
    if response.status_code != 200:
        return None

    try:
        payload = response.json()
    except ValueError:
        return None
    try:
        user_id = UUID(payload["id"])
        email = payload["email"]
    except (KeyError, TypeError, ValueError):
        return None
    if not isinstance(email, str) or email == "":
        return None
    return CurrentUser(user_id=user_id, email=email)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CurrentUser:
    if credentials is None or credentials.credentials == "":
        raise _unauthorized()

    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            user = await fetch_auth_user(
                credentials.credentials, settings, http_client
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service unavailable",
        ) from exc

    if user is None:
        raise _unauthorized()
    if not is_allowed_email(user.email, settings.allowed_email_domain):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use your Driftwood email.",
        )
    return user
