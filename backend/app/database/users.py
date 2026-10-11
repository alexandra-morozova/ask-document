from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from supabase import AsyncClient

from app.auth.dependencies import CurrentUser, bearer_scheme, get_current_user
from app.config import Settings, get_settings
from app.database.supabase import create_user_client


@dataclass(frozen=True, slots=True)
class UserRow:
    id: UUID
    email: str


def _parse_row(data: object, user: CurrentUser) -> UserRow | None:
    if not isinstance(data, dict):
        return None
    try:
        row_id = UUID(data["id"])
        email = data["email"]
    except (KeyError, TypeError, ValueError):
        return None
    if row_id != user.user_id or not isinstance(email, str) or email == "":
        return None
    return UserRow(id=row_id, email=email)


async def get_user(client: AsyncClient, user: CurrentUser) -> UserRow | None:
    result = await (
        client.table("users")
        .select("id, email")
        .eq("id", str(user.user_id))
        .maybe_single()
        .execute()
    )
    return _parse_row(result.data, user)


async def create_user(client: AsyncClient, user: CurrentUser) -> UserRow:
    await (
        client.table("users")
        .upsert(
            {"id": str(user.user_id), "email": user.email},
            on_conflict="id",
        )
        .execute()
    )
    return UserRow(id=user.user_id, email=user.email)


async def ensure_app_user(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserRow:
    assert credentials is not None
    client = await create_user_client(settings, credentials.credentials)
    existing = await get_user(client, user)
    if existing is not None:
        return existing
    return await create_user(client, user)
