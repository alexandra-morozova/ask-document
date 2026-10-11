import asyncio
from inspect import signature
from uuid import UUID

from app.config import Settings
from app.database.supabase import create_admin_client, create_user_client

_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def _settings() -> Settings:
    return Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon-key",
        supabase_service_role_key="service-key",
        database_url="postgresql://localhost/test",
        openai_api_key="sk-test",
        allowed_origins=["http://localhost:5173"],
        openai_embedding_model="text-embedding-3-small",
        openai_embedding_dimensions=1536,
    )


def test_admin_client_requires_authenticated_user_id() -> None:
    assert "user_id" in signature(create_admin_client).parameters

    admin = asyncio.run(create_admin_client(_settings(), _USER_ID))

    assert admin.user_id == _USER_ID
    assert admin.client.supabase_key == "service-key"
    assert admin.client.options.headers["Authorization"] == "Bearer service-key"
    assert admin.client.options.headers["apiKey"] == "service-key"


def test_user_client_uses_anon_key_and_user_jwt() -> None:
    client = asyncio.run(create_user_client(_settings(), "user-jwt"))

    assert client.supabase_key == "anon-key"
    assert client.options.headers["Authorization"] == "Bearer user-jwt"
    assert client.options.headers["apiKey"] == "anon-key"
    assert "service-key" not in client.options.headers.values()
