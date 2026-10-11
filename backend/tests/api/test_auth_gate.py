from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router
from app.config import Settings, get_settings
from app.database.users import ensure_app_user


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


def test_api_router_requires_current_user() -> None:
    assert [dep.dependency for dep in api_router.dependencies] == [ensure_app_user]


def test_unauthenticated_request_does_not_reach_handler() -> None:
    called = False
    app = FastAPI()
    app.dependency_overrides[get_settings] = _settings
    router = APIRouter(dependencies=list(api_router.dependencies))

    @router.get("/retrieve")
    async def retrieve() -> dict[str, str]:
        nonlocal called
        called = True
        return {"status": "retrieved"}

    app.include_router(router)
    response = TestClient(app).get("/retrieve")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid token"
    assert called is False


def test_health_stays_public() -> None:
    app = FastAPI()
    app.dependency_overrides[get_settings] = _settings
    app.include_router(api_router)

    @app.get("/")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
