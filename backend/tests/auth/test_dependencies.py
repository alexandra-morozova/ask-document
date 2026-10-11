import asyncio
from uuid import UUID

import httpx
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentUser, fetch_auth_user, get_current_user
from app.config import Settings, get_settings

_USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "supabase_url": "https://example.supabase.co",
        "supabase_anon_key": "anon-key",
        "supabase_service_role_key": "service-key",
        "database_url": "postgresql://localhost/test",
        "openai_api_key": "sk-test",
        "allowed_origins": ["http://localhost:5173"],
        "allowed_email_domain": None,
        "openai_embedding_model": "text-embedding-3-small",
        "openai_embedding_dimensions": 1536,
    }
    values.update(overrides)
    return Settings.model_validate(values)


def _client_for(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_fetch_auth_user_returns_current_user() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://example.supabase.co/auth/v1/user"
        assert request.headers["authorization"] == "Bearer user-jwt"
        assert request.headers["apikey"] == "anon-key"
        return httpx.Response(
            200,
            json={"id": str(_USER_ID), "email": "analyst@example.com"},
        )

    async def run() -> CurrentUser | None:
        async with _client_for(handler) as http_client:
            return await fetch_auth_user("user-jwt", _settings(), http_client)

    assert asyncio.run(run()) == CurrentUser(
        user_id=_USER_ID, email="analyst@example.com"
    )


def test_fetch_auth_user_rejects_non_200() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "invalid"})

    async def run() -> CurrentUser | None:
        async with _client_for(handler) as http_client:
            return await fetch_auth_user("bad", _settings(), http_client)

    assert asyncio.run(run()) is None


def test_fetch_auth_user_raises_on_auth_5xx() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    async def run() -> CurrentUser | None:
        async with _client_for(handler) as http_client:
            return await fetch_auth_user("user-jwt", _settings(), http_client)

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(run())


def test_fetch_auth_user_rejects_non_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json")

    async def run() -> CurrentUser | None:
        async with _client_for(handler) as http_client:
            return await fetch_auth_user("user-jwt", _settings(), http_client)

    assert asyncio.run(run()) is None


def test_fetch_auth_user_rejects_malformed_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "not-a-uuid", "email": "x@y.z"})

    async def run() -> CurrentUser | None:
        async with _client_for(handler) as http_client:
            return await fetch_auth_user("user-jwt", _settings(), http_client)

    assert asyncio.run(run()) is None


def _default_settings() -> Settings:
    return _settings()


def _app(settings_factory=_default_settings) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_settings] = settings_factory

    @app.get("/me")
    async def me(user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:
        return {"user_id": str(user.user_id), "email": user.email}

    return app


def test_get_current_user_401_without_bearer() -> None:
    response = TestClient(_app()).get("/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid token"


def test_get_current_user_401_when_auth_rejects_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(
        token: str, settings: Settings, http_client: httpx.AsyncClient
    ) -> CurrentUser | None:
        return None

    monkeypatch.setattr("app.auth.dependencies.fetch_auth_user", fake_fetch)
    response = TestClient(_app()).get("/me", headers={"Authorization": "Bearer bad"})
    assert response.status_code == 401


def test_get_current_user_returns_verified_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(
        token: str, settings: Settings, http_client: httpx.AsyncClient
    ) -> CurrentUser | None:
        assert token == "user-jwt"
        return CurrentUser(user_id=_USER_ID, email="analyst@example.com")

    monkeypatch.setattr("app.auth.dependencies.fetch_auth_user", fake_fetch)
    response = TestClient(_app()).get(
        "/me", headers={"Authorization": "Bearer user-jwt"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "user_id": str(_USER_ID),
        "email": "analyst@example.com",
    }


def test_get_current_user_502_when_auth_is_down(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(
        token: str, settings: Settings, http_client: httpx.AsyncClient
    ) -> CurrentUser | None:
        raise httpx.ConnectError("auth down")

    monkeypatch.setattr("app.auth.dependencies.fetch_auth_user", fake_fetch)
    response = TestClient(_app()).get(
        "/me", headers={"Authorization": "Bearer user-jwt"}
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "Auth service unavailable"


def test_get_current_user_403_when_email_domain_not_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(
        token: str, settings: Settings, http_client: httpx.AsyncClient
    ) -> CurrentUser | None:
        return CurrentUser(user_id=_USER_ID, email="analyst@example.com")

    monkeypatch.setattr("app.auth.dependencies.fetch_auth_user", fake_fetch)
    response = TestClient(
        _app(lambda: _settings(allowed_email_domain="driftwood.com"))
    ).get("/me", headers={"Authorization": "Bearer user-jwt"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Use your Driftwood email."


def test_get_current_user_allows_matching_email_domain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(
        token: str, settings: Settings, http_client: httpx.AsyncClient
    ) -> CurrentUser | None:
        return CurrentUser(user_id=_USER_ID, email="analyst@example.com")

    monkeypatch.setattr("app.auth.dependencies.fetch_auth_user", fake_fetch)
    response = TestClient(
        _app(lambda: _settings(allowed_email_domain="example.com"))
    ).get("/me", headers={"Authorization": "Bearer user-jwt"})
    assert response.status_code == 200
