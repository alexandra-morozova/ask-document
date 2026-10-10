# Backend

FastAPI service for Document Copilot. Env is read only through `app/config.py` (`get_settings()`). Do not call `os.getenv` or `load_dotenv` in app code.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (installs and pins Python 3.12 for this project)
- A `backend/.env` file with the required variables below (copy from `.env.example`)
- Hosted Supabase project and an OpenAI API key

Python itself does not need to be installed system-wide. From `backend/`:

```bash
uv python install 3.12
uv sync
```

## Commands

Run all of these from `backend/`.

```bash
uv sync
```

Install runtime and dev dependencies into `.venv`.

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the API. Loads settings on import and exits if required env is missing.

`GET /` returns `{"status": "ok"}`. There are no product routes yet.

```bash
uv run pytest
uv run pytest -m "not integration"
```

`pytest` runs everything under `tests/`. The fast suite skips `@pytest.mark.integration` tests (live network, database, or API credentials). Prefer that for day-to-day work.

```bash
uv run ruff check
uv run ruff check --fix
```

Lint `app/`, `ingest/`, `tests/`, and `alembic/`. `--fix` applies safe autofixes (including import order).

```bash
uv run alembic heads
uv run alembic upgrade head
```

Alembic reads `DATABASE_URL` from `app.config`. No migration has been generated yet. Use the Supabase **direct/session** URL, not the transaction pooler.
