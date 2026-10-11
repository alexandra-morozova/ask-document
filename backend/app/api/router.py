from fastapi import APIRouter, Depends

from app.database.users import ensure_app_user

# Product routes share this router so auth runs before any retrieval or LLM work.
api_router = APIRouter(dependencies=[Depends(ensure_app_user)])
