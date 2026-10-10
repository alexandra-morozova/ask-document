from fastapi import FastAPI

from app.config import get_settings

app = FastAPI(title="Document Copilot")
app.state.settings = get_settings()


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok"}

