from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.auth.access import require_thread_owner
from app.auth.dependencies import CurrentUser

_OWNER = UUID("11111111-1111-1111-1111-111111111111")
_OTHER = UUID("22222222-2222-2222-2222-222222222222")
_USER = CurrentUser(user_id=_OWNER, email="analyst@example.com")


def test_owner_is_allowed() -> None:
    require_thread_owner(_OWNER, _USER)


def test_other_user_is_forbidden() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_thread_owner(_OTHER, _USER)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not allowed to access this thread"


def test_handler_does_not_run_for_another_users_thread() -> None:
    called = False
    app = FastAPI()

    @app.get("/threads/{thread_id}")
    async def read_thread() -> dict[str, str]:
        nonlocal called
        require_thread_owner(_OTHER, _USER)
        called = True
        return {"status": "ok"}

    response = TestClient(app).get(
        "/threads/33333333-3333-3333-3333-333333333333"
    )

    assert response.status_code == 403
    assert called is False
