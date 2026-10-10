# Document Copilot — implementation todo

Work through these in order. Later items depend on earlier ones. Check a box only when the item is done and verifiable.

This list exists to satisfy [architecture.md](architecture.md) and [client-brief.md](client-brief.md): a thin React SPA, an authoritative FastAPI backend, hybrid retrieval over a curated SEC corpus, and grounded answers that analysts can trust.

---

## 0. Product contract (do not skip)

These are invariants, not polish. Every later phase must preserve them.

- [ ] Answers are generated only from retrieved source passages.
- [ ] Every factual claim is citable to a specific filing and page or section.
- [ ] If the corpus does not support an answer, the bot says so clearly instead of inferring.
- [ ] The bot never gives stock recommendations, stock picks, or investment advice.
- [ ] The bot never uses news, social, or any data outside the ingested SEC corpus.
- [ ] A wrong-but-confident answer is treated as a product failure.
- [ ] The browser never holds the service-role key, never calls OpenAI, and never runs retrieval.
- [ ] All privileged writes are tied to the authenticated user.

---

## 1. Scaffold the apps

Follow repo conventions in `AGENTS.md`, `backend/AGENTS.md`, and `frontend/AGENTS.md`.

### Backend
- [x] Create gitignore
- [x] Create `backend/` as a `uv` project (Python 3.12+).
- [x] Add FastAPI + Uvicorn, Pydantic v2, pydantic-settings, `httpx`, `structlog`, OpenAI SDK, Supabase Python client, SQLAlchemy, Alembic, PydanticAI, pytest, ruff.
- [x] Add `app/main.py` FastAPI entrypoint and `app/config.py` as the only env source of truth.
- [x] Fail fast on startup if required backend env is missing: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, `OPENAI_API_KEY`, `ALLOWED_ORIGINS`, embedding model name and dimensions.
- [x] Do not call `os.getenv` or `load_dotenv` in app code.
- [x] Add empty module layout: `api/`, `auth/`, `chat/`, `assistant/`, `retrieval/`, `grounding/`, `database/`, `ingest/`, `tests/`.
- [x] Create unit tests setup with Ruff 

### Frontend
- [x] Create gitignore
- [x] Create `frontend/` as a Vite + React + TypeScript SPA (`pnpm` only).
- [x] Add React Router, Tailwind, shadcn/ui, `@supabase/supabase-js`, and Vercel AI SDK UI packages.
- [x] Add `src/lib/env.ts` that validates `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` at boot.
- [x] Never read `import.meta.env` outside `src/lib/env.ts`.
- [x] Do not introduce Next.js, SSR, server components, or frontend route handlers.
- [x] Add route shell: sign-in page and a placeholder chat page.

### Shared

- [x] Add example env files for both services (no secrets committed).
- [x] Confirm local frontend and backend start independently.

---

## 2. Database schema and migrations

Supabase is hosted Postgres. Alembic is the source of truth. Do not define tables only in the dashboard.

- [x] Add SQLAlchemy models in `backend/app/database/models/` for:
  - [x] `users` (one row per `auth.users.id`)
  - [x] `chat_threads` (owner, title, timestamps)
  - [x] `chat_messages` (ordered user/assistant messages; store AI SDK-compatible JSON where useful)
  - [x] `message_citations` (normalized citations linked to assistant messages)
  - [x] `source_documents` (filing metadata, source URL, normalized Markdown)
  - [x] `document_chunks` (chunk text, index, page/section metadata, embedding, `tsvector`, token count, ticker/company/filing metadata JSON)
- [x] Configure Alembic (`alembic.ini`, `alembic/env.py`) to import app metadata.
- [x] Point Alembic at the Supabase **direct/session** `DATABASE_URL`, not the transaction pooler.
- [x] Generate, review, and apply the initial migration.
- [x] Add explicit migration operations that autogenerate cannot infer:
  - [x] `create extension if not exists vector`
  - [x] `vector(1536)` embedding column (or configured dimensions)
  - [x] generated `tsvector` column on `document_chunks`
  - [x] HNSW index for vector search
  - [x] GIN indexes for full-text search and JSON metadata
  - [x] RLS enablement and policies
  - [x] grants / Supabase role permissions
- [x] Commit models and the reviewed migration together.

---

## 3. Auth and user-scoped access

Login is Driftwood email via Supabase Auth. No SSO.

- [ ] Create the browser Supabase client in `frontend/src/lib/supabase.ts` (anon key only).
- [ ] Add email sign-in / sign-out UI. Session lives in `@supabase/supabase-js`.
- [ ] Restrict signup/login to Driftwood email addresses if a domain allowlist is available; otherwise document the manual invite path for ~40 analysts.
- [ ] Add `backend/app/auth/dependencies.py` that verifies `Authorization: Bearer <token>` by calling Supabase Auth's user endpoint.
- [ ] Reject unauthenticated requests before retrieval or LLM work (`401`).
- [ ] Derive `user_id` and email from the verified user.
- [ ] Create user-scoped and admin Supabase clients in `backend/app/database/supabase.py`.
- [ ] Use the service-role key only on the backend, and only for privileged writes that still attach the authenticated `user_id`.
- [ ] Ensure a user cannot read or write another user's threads (`403`).
- [ ] Create/read `users` for the authenticated user.

---

## 4. Shared frontend API client

- [ ] Add `frontend/src/lib/http.ts`: base URL, bearer-token injection, timeouts, typed API errors.
- [ ] Distinguish network/CORS failures from HTTP failures (`isNetworkError`).
- [ ] Add `frontend/src/lib/api.ts` product calls: list threads, create thread, load message history, load a source passage.
- [ ] Never pass tokens through component props.
- [ ] Map backend errors to friendly UI copy while logging enough technical detail:
  - [ ] `401` missing/expired/invalid token
  - [ ] `403` another user's thread
  - [ ] `404` missing thread or document
  - [ ] `422` invalid payload
  - [ ] `502` upstream LLM or Supabase failure
  - [ ] `500` unexpected backend failure

---

## 5. Chat persistence and stub streaming

Build the chat path before retrieval so the UI can be wired end to end.

### Backend

- [ ] Add `backend/app/database/chats.py` for threads, messages, and citations.
- [ ] Add FastAPI routes in `backend/app/api/chat.py`:
  - [ ] create thread
  - [ ] list current user's threads
  - [ ] load thread + messages (user-scoped)
  - [ ] `POST /chat/stream` with `{ threadId, messages }`
- [ ] Translate AI SDK UI messages into internal Pydantic models (`backend/app/chat/messages.py`).
- [ ] Emit AI SDK-compatible streaming events (`backend/app/chat/streaming.py`).
- [ ] Stub the assistant: stream a fixed response so the frontend can be built without OpenAI.
- [ ] Persist user + assistant messages only after a successful run (no partial-message model yet).
- [ ] Return clear stream error events for auth, missing thread, and unexpected failures.

### Frontend

- [ ] Load the user's thread list and past conversations on the chat page.
- [ ] Create a new thread and restore prior messages when opening one.
- [ ] Point Vercel AI SDK `useChat` at FastAPI `/chat/stream` with the Supabase bearer token.
- [ ] Verify the exact AI SDK transport API against the installed version.
- [ ] Render streaming status, empty states, and errors.

---

## 6. Ingestion pipeline

Corpus is SEC EDGAR 10-K/10-Q filings. Sample set: AAPL, AMZN, GOOGL, MSFT, NVDA, fiscal years 2021–2025. `data/download.py` already downloads raw filings.

- [ ] Keep raw downloads gitignored; do not store them in Railway.
- [ ] Add Markdown extraction from downloaded HTML/filing files (`backend/ingest/`).
- [ ] Store normalized Markdown on `source_documents` with filing metadata: ticker, company, filing type, filing date, year, accession number, source URL.
- [ ] Chunk filings into retrieval-ready passages with page or section metadata and source offsets.
- [ ] Embed chunks with the configured OpenAI embedding model.
- [ ] Write documents, chunks, embeddings, and generated full-text vectors to Supabase.
- [ ] Make ingestion re-runnable: skip unchanged filings, fail clearly on parse/embed errors.
- [ ] Add unit tests for parse, chunk, and metadata extraction (no network).
- [ ] Ingest the sample 5-company 10-K corpus and confirm documents + chunks are queryable.

---

## 7. Hybrid retrieval

Retrieval stays independent of PydanticAI so it can be tested without the LLM.

- [ ] Add `backend/app/retrieval/queries.py`:
  - [ ] embed the user query
  - [ ] semantic search over `document_chunks.embedding` with `pgvector`
  - [ ] lexical search over `document_chunks.search_vector` with Postgres full-text
- [ ] Add Reciprocal Rank Fusion in `backend/app/retrieval/fusion.py`.
- [ ] Add `backend/app/retrieval/retriever.py` that returns bounded source passages plus neighboring chunks.
- [ ] Fetch selected chunks with document metadata (company, filing, date, page/section, excerpt).
- [ ] Do not let the agent generate SQL. Expose only bounded tools later: `search_filings`, `read_chunk`, `read_surrounding_chunks`.
- [ ] Add unit tests for ranking, fusion, and passage assembly.
- [ ] Mark any live-DB checks `@pytest.mark.integration`.

---

## 8. PydanticAI document agent

- [ ] Add typed deps in `backend/app/assistant/deps.py` (`user_id`, `thread_id`, retriever, grounding validator).
- [ ] Add typed outputs in `backend/app/assistant/outputs.py`: `GroundedAnswer`, `Citation`, `SourcePassage`.
- [ ] Write `backend/app/assistant/instructions.md` with the product contract:
  - [ ] answer only from retrieved passages
  - [ ] cite every factual claim
  - [ ] refuse when evidence is insufficient
  - [ ] no investment advice
  - [ ] concise enough for analyst review, with enough cited passages to verify
- [ ] Define the agent in `backend/app/assistant/agent.py` with explicit dependencies and bounded tools.
- [ ] Add `backend/app/chat/orchestrator.py` to own one full turn: auth context, retrieve, generate, validate, stream, persist.
- [ ] Replace the stub stream with the real agent.
- [ ] Stream text deltas as they are generated.
- [ ] Stream citation/source metadata as structured parts once available.
- [ ] Persist the final answer, cited chunks, and usage metadata.

---

## 9. Grounding and citation enforcement

Grounding is architecture, not a prompt preference.

- [ ] Add `backend/app/grounding/validator.py`.
- [ ] Enforce: every assistant answer has at least one citation unless it explicitly says there is not enough evidence.
- [ ] Enforce: every citation maps to a passage retrieved for this request.
- [ ] Reject citations to documents that were not retrieved.
- [ ] Cited passages include company, filing, date, page or section, and excerpt.
- [ ] If validation fails, return a controlled failure (`502` / stream error), not a polished unsupported answer.
- [ ] Add unit tests for citation extraction, mapping, and grounding failure cases.

---

## 10. Analyst chat UI

The analyst must be able to verify an answer in one click.

- [ ] Render assistant answers with inline citations.
- [ ] Show filing identity: company, form type, year/date, page or section.
- [ ] Clicking a citation reveals the underlying passage excerpt.
- [ ] Empty states for no threads, no corpus hits, and insufficient evidence.
- [ ] Streaming status while the assistant is retrieving / generating.
- [ ] Error states that distinguish auth, network/CORS, missing thread, retrieval, and grounding failures.
- [ ] Thread sidebar: own past conversations only, titled, newest first.
- [ ] Desktop-first browser UI (no mobile app). Keep the layout usable on a laptop.

---

## 11. Trust behavior for the sample questions

The bot must handle the brief's example questions with cited passages. These are the acceptance prompts, not a separate feature.

For each question, confirm: cited answer, visible passages, and a refusal when the filings do not prove the claim.

- [ ] Apple 2021–2025 revenue mix across iPhone, Services, Mac, iPad, Wearables — what shifted, and which category drove it.
- [ ] Amazon AWS operating income/margin vs North America and International, 2021–2025 — years AWS appears to fund weaker profitability elsewhere.
- [ ] NVIDIA Data Center demand drivers, customer concentration, and supply constraints, FY2021–FY2025.
- [ ] Microsoft language changes around Azure, AI infrastructure, and cloud capacity constraints, 2021–2025.
- [ ] Alphabet revenue trends for Search, YouTube ads, Google Network, subscriptions/platforms/devices, and Google Cloud.
- [ ] Which of the five companies added, removed, or materially changed risk-factor language on AI, cloud infrastructure, export controls, supply chain concentration, or regulation.
- [ ] Apple and NVIDIA supplier concentration / third-party manufacturing — wording more or less urgent over time.
- [ ] Capex and purchase commitments for Microsoft, Alphabet, Amazon, and NVIDIA — scale and timing of AI/cloud investment.
- [ ] Latest 10-K geographic revenue exposures per company, plus year-over-year changes that could matter.
- [ ] “Do the filings prove generative AI improved margins?” — show existing evidence and refuse to infer beyond the corpus.

---

## 12. Deploy on a small cloud footprint

Driftwood has no infra team. Keep it to Railway + hosted Supabase.

- [ ] Railway frontend service: static Vite build.
- [ ] Railway backend service: FastAPI + Uvicorn, stateless.
- [ ] Backend CORS limited to `ALLOWED_ORIGINS`.
- [ ] Supabase holds users, chats, documents, chunks, embeddings, full-text vectors, citations.
- [ ] Raw filings stay local/gitignored unless a later workflow adds object storage.
- [ ] Document required env vars and a one-pass deploy checklist in the repo README.
- [ ] Invite the 5-analyst pilot with Driftwood email accounts.

---

## 13. Pilot definition of done

The architecture is not done until the brief's pilot test can run.

- [ ] 5 senior analysts can sign in with Driftwood email and use the chatbot from a browser.
- [ ] They can ask plain-English questions over the curated corpus and get sourced answers.
- [ ] They can open the cited filing passage and verify the claim.
- [ ] They can see their own past conversations after coming back later.
- [ ] The bot refuses when the corpus does not contain enough evidence.
- [ ] The bot does not produce trading recommendations.
- [ ] After one week, the pilot reports at least 3 hours saved per analyst per week. If yes, roll out firm-wide (~40 analysts + a few partners).

---

## Explicitly out of scope

Do not pick these up unless the brief or architecture changes.

- Next.js, SSR, frontend route handlers, or a Node BFF
- Direct OpenAI calls from the browser
- A vector database other than Supabase `pgvector`
- Multi-tenant / multi-client product
- Billing, plans, paywalls
- Mobile app
- External market, news, or alternative data
- Trading recommendations or generated stock picks
- Agent-generated SQL
- Partial-message persistence (unless deliberately added later)
- Local JWT verification (Auth user-endpoint check is enough for v1)
