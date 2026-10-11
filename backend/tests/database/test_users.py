import asyncio
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import CurrentUser
from app.config import Settings
from app.database.users import UserRow, create_user, ensure_app_user, get_user

_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
_OTHER_ID = UUID("22222222-2222-2222-2222-222222222222")
_USER = CurrentUser(user_id=_USER_ID, email="analyst@example.com")


class FakeQuery:
    def __init__(self, data: object) -> None:
        self.data = data
        self.calls: list[tuple[object, ...]] = []

    def select(self, *columns: str) -> "FakeQuery":
        self.calls.append(("select", columns))
        return self

    def eq(self, column: str, value: object) -> "FakeQuery":
        self.calls.append(("eq", column, value))
        return self

    def maybe_single(self) -> "FakeQuery":
        self.calls.append(("maybe_single",))
        return self

    def upsert(self, row: dict[str, str], **kwargs: object) -> "FakeQuery":
        self.calls.append(("upsert", row, kwargs.get("on_conflict")))
        return self

    async def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self.data)


class FakeClient:
    def __init__(self, query: FakeQuery) -> None:
        self.query = query

    def table(self, name: str) -> FakeQuery:
        assert name == "users"
        return self.query


def test_get_user_reads_authenticated_row() -> None:
    query = FakeQuery({"id": str(_USER_ID), "email": "analyst@example.com"})
    row = asyncio.run(get_user(FakeClient(query), _USER))  # type: ignore[arg-type]

    assert row == UserRow(id=_USER_ID, email="analyst@example.com")
    assert ("eq", "id", str(_USER_ID)) in query.calls


def test_get_user_returns_none_when_missing() -> None:
    query = FakeQuery(None)
    assert asyncio.run(get_user(FakeClient(query), _USER)) is None  # type: ignore[arg-type]


def test_get_user_ignores_another_users_row() -> None:
    query = FakeQuery({"id": str(_OTHER_ID), "email": "other@example.com"})
    assert asyncio.run(get_user(FakeClient(query), _USER)) is None  # type: ignore[arg-type]


def test_create_user_upserts_authenticated_id_and_email() -> None:
    query = FakeQuery([])
    row = asyncio.run(create_user(FakeClient(query), _USER))  # type: ignore[arg-type]

    assert row == UserRow(id=_USER_ID, email="analyst@example.com")
    assert (
        "upsert",
        {"id": str(_USER_ID), "email": "analyst@example.com"},
        "id",
    ) in query.calls


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


def test_ensure_app_user_reads_existing_row(monkeypatch: pytest.MonkeyPatch) -> None:
    created = False
    existing = UserRow(id=_USER_ID, email="analyst@example.com")

    async def fake_client(settings: Settings, access_token: str):
        return object()

    async def fake_get(client: object, user: CurrentUser) -> UserRow | None:
        return existing

    async def fake_create(client: object, user: CurrentUser) -> UserRow:
        nonlocal created
        created = True
        return existing

    monkeypatch.setattr("app.database.users.create_user_client", fake_client)
    monkeypatch.setattr("app.database.users.get_user", fake_get)
    monkeypatch.setattr("app.database.users.create_user", fake_create)

    row = asyncio.run(
        ensure_app_user(
            _USER,
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="user-jwt"),
            _settings(),
        )
    )
    assert row == existing
    assert created is False


def test_ensure_app_user_creates_missing_row(monkeypatch: pytest.MonkeyPatch) -> None:
    created = UserRow(id=_USER_ID, email="analyst@example.com")

    async def fake_client(settings: Settings, access_token: str):
        assert access_token == "user-jwt"
        return object()

    async def fake_get(client: object, user: CurrentUser) -> UserRow | None:
        return None

    async def fake_create(client: object, user: CurrentUser) -> UserRow:
        assert user is _USER
        return created

    monkeypatch.setattr("app.database.users.create_user_client", fake_client)
    monkeypatch.setattr("app.database.users.get_user", fake_get)
    monkeypatch.setattr("app.database.users.create_user", fake_create)

    row = asyncio.run(
        ensure_app_user(
            _USER,
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="user-jwt"),
            _settings(),
        )
    )
    assert row == created
