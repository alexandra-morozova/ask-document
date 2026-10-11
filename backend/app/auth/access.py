from uuid import UUID

from fastapi import HTTPException, status

from app.auth.dependencies import CurrentUser


def require_thread_owner(owner_id: UUID, user: CurrentUser) -> None:
    if owner_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this thread",
        )
