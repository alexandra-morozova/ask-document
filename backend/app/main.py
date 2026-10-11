from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings

app = FastAPI(title="Document Copilot")
app.state.settings = get_settings()
app.include_router(api_router)


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok"}

