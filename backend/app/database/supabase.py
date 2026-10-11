from dataclasses import dataclass
from uuid import UUID

from supabase import AsyncClient, AsyncClientOptions, acreate_client

from app.config import Settings


def _options(*, access_token: str | None = None) -> AsyncClientOptions:
    headers = {}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"
    return AsyncClientOptions(
        headers=headers,
        auto_refresh_token=False,
        persist_session=False,
    )


@dataclass(frozen=True, slots=True)
class AdminClient:
    """Service-role client. RLS is bypassed; every write must use user_id."""

    client: AsyncClient
    user_id: UUID


async def create_admin_client(settings: Settings, user_id: UUID) -> AdminClient:
    client = await acreate_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
        _options(),
    )
    return AdminClient(client=client, user_id=user_id)


async def create_user_client(settings: Settings, access_token: str) -> AsyncClient:
    # Anon key + user JWT so PostgREST applies RLS as that user.
    return await acreate_client(
        settings.supabase_url,
        settings.supabase_anon_key,
        _options(access_token=access_token),
    )
