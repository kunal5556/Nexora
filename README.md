# Nexora – LLM Chatbot with Key Failover and Response Caching

A small full-stack chat app built for the Lyftr AI full-stack assignment. You chat with a Gemini model in the browser, and every reply shows where it came from (live call or cache), which model answered, how long the request took and how many tokens that one request used. Behind the scenes the backend keeps a pool of API keys, switches to the next key automatically when one is rate-limited, out of quota or failing, and answers repeated requests from LiteLLM's cache.

**Stack:** React 19 + Vite + Tailwind CSS (frontend) · Python 3.12 + FastAPI + LiteLLM (backend) · SQLite (storage) · Docker Compose + Make (local run) · Render + Vercel (deployment)

```
Browser (React) ──JSON──▶ FastAPI routes ──▶ chat_service ──▶ llm_gateway ──▶ LiteLLM ──▶ Gemini (key_1, key_2)
                                                  │                              │
                                                  ▼                              └── LiteLLM in-memory cache
                                         SQLite (/data/app.db)
```

```
backend/
  app/            config, database, schemas, chat_service, llm_gateway, failure_simulation, routes, main
  tests/          pytest suite (69 tests)
  scripts/        smoke_test.py – end-to-end contract check against a running backend
frontend/
  src/            App.jsx, api.js, components/ (header, settings, message list, bubbles, metadata, input)
docker-compose.yml, Makefile, .env.example
```

## 1. Live URLs

| | URL |
|---|---|
| Frontend (Vercel) | https://nexora-llm-chatbot.vercel.app |
| Backend (Render) | https://nexora-backend-owc8.onrender.com |
| Health check | https://nexora-backend-owc8.onrender.com/health |
| Repository | https://github.com/kunal5556/Nexora |

The backend runs on Render's free plan, which goes to sleep after about 15 minutes without traffic. The first request after that can take up to a minute while it wakes up; after that it responds normally.

## 2. Run locally

### With Docker

You need Docker Desktop (Compose v2), GNU Make and two Gemini API keys. The keys are free from Google AI Studio; creating them in two different Google Cloud projects gives each key its own quota.

1. Copy the example env file and put your keys in it:
   ```bash
   cp .env.example .env
   ```
   (On Windows: `copy .env.example .env`.) Then edit `.env` and set `LLM_API_KEYS=first-key,second-key`.
2. Start everything:
   ```bash
   make up
   ```
3. Open http://localhost:3000 for the chat UI. The API is on http://localhost:8000.
4. `make logs` follows the logs and `make down` stops everything.

Chat history is stored in SQLite at `/data/app.db` inside the named volume `chat_data`, so it survives `make down` followed by `make up`.

### Without Docker

You need Python 3.12 and Node.js 22.12 or newer. The backend reads the same `.env` file from the repository root.

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=sqlite:///./data/app.db
uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell use `.venv\Scripts\activate` and `$env:DATABASE_URL = "sqlite:///./data/app.db"` instead. `DATABASE_URL` is overridden here because the value in `.env` points to the Docker volume path.

Frontend, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000.

Tests and the unused-code check, from `backend/`:

```bash
python -m pytest
python -m ruff check --select F .
```

### Environment variables

| Variable | Used by | Example | What it does |
|---|---|---|---|
| `LLM_API_KEYS` | backend | `key-one,key-two` | Comma-separated key pool, at least 2 keys. Key ids are `key_1`, `key_2`, … in this order. The app refuses to start with fewer than 2. |
| `LLM_MODEL` | backend | `gemini/gemini-3.5-flash-lite` | LiteLLM model name used with every key. |
| `DATABASE_URL` | backend | `sqlite:////data/app.db` | SQLite file location (`sqlite:///` followed by the path). |
| `ALLOWED_ORIGINS` | backend | `http://localhost:3000` | Comma-separated CORS origins. |
| `ENABLE_FAILURE_SIMULATION` | backend | `true` | Enables the `X-Simulate-Failure` header. Any other value turns it off. |
| `DEFAULT_SYSTEM_PROMPT` | backend | `You are a helpful assistant. …` | System prompt used when a session doesn't set its own. |
| `CACHE_TTL_SECONDS` | backend | `86400` | How long a cached LLM response stays valid. |
| `LLM_TIMEOUT_SECONDS` | backend | `30` | Timeout for one attempt with one key. |
| `LITELLM_LOCAL_MODEL_COST_MAP` | LiteLLM | `True` | Makes LiteLLM use its bundled model list instead of downloading it at startup. |
| `VITE_API_BASE_URL` | frontend build | `http://localhost:8000` | Backend URL baked into the frontend when it is built. |
| `PORT` | backend container | set by Render | Port uvicorn listens on (8000 when not set). |

## 3. Design decisions

### Key fallback

- Every key in the pool uses the same model (`LLM_MODEL`), so an answer cached through one key is valid for all of them.
- `llm_gateway.ask_llm()` tries the keys **in order**: `key_1`, then `key_2`, and so on. Each attempt is one `litellm.completion()` call with that key, `num_retries=0` and a timeout, so a failing key is given up on quickly instead of being retried.
- LiteLLM turns provider errors into typed exceptions that carry a `status_code`: `RateLimitError` (429, which is also how Gemini reports an exhausted quota), `InternalServerError` (500), `BadGatewayError` (502), `ServiceUnavailableError` (503), `AuthenticationError` (401), timeouts and so on. Any exception, or an empty reply, counts as a failed attempt and the loop moves on to the next key. That covers the required 429 / quota / 5xx cases and also revoked or invalid keys.
- `key_id` is the id of the key that answered and `fallback_attempts` is how many keys failed before it. The key itself is never returned, stored or logged; the log only says things like `key_1 failed with status 429, trying next key`.
- If every key fails, the gateway raises `AllProvidersUnavailableError`, and a FastAPI exception handler turns it into `503 {"detail": "all providers unavailable"}`. Nothing is saved, because the database write only happens after a successful reply.
- LiteLLM's `Router` was considered, but the test hook needs "fail exactly these keys with exactly these status codes, for this one request", and the response has to say exactly which key answered and how many failed first. The Router chooses deployments itself, keeps cooldowns between requests and doesn't report attempts, which makes that hard to control. A short loop over `litellm.completion()` keeps LiteLLM in charge of the provider calls, error mapping and caching, while the order stays predictable and easy to follow.

### Caching

- On startup the backend enables LiteLLM's built-in in-memory cache: `litellm.cache = Cache(type="local", ttl=CACHE_TTL_SECONDS)`.
- LiteLLM builds the cache key from the model and the full message list (system prompt + history + new message). The API key, `timeout` and `num_retries` are not part of the key, so a cached answer is reused no matter which key would have been tried.
- The client sends only the new message and the backend adds the default system prompt, so the same first message in a new session produces exactly the same message list and comes back as `LLM_CACHE`. A different message, or a different history, is a different key and becomes `LIVE_INFERENCE`.
- A cache hit is detected with `response._hidden_params["cache_hit"]`. On a hit the reply text and the token usage are the ones stored with the cached response, `key_id` is `null` and `fallback_attempts` is `0`.
- Requests that carry an active `X-Simulate-Failure` header skip the cache **read** (`cache={"no-cache": True}`) but still write their answer to the cache. Otherwise a message that was cached earlier would never reach the "failing" key and the failover demo would show nothing.
- Trade-off: the in-memory cache is emptied when the backend restarts and holds up to 200 entries (LiteLLM's default). For this project that is fine and keeps everything in one process with no extra services. LiteLLM's disk cache would be a one-line change if it ever needs to survive restarts.

### SQLite session storage

- `DATABASE_URL` points to the SQLite file. In Docker it is `/data/app.db` on the named volume `chat_data`, so history survives container restarts. The schema is created on startup with `CREATE TABLE IF NOT EXISTS`.
- The `messages` table has exactly the columns from the brief (`id, session_id, role, content, metadata, created_at`) plus an index on `(session_id, id)`. Assistant rows store their full metadata as a JSON string; `created_at` is server time in ISO-8601 (UTC).
- A small extra `sessions` table remembers a session's custom `system_prompt`, so it keeps applying to later messages in that session even if the client sends it only once.
- One chat turn is saved in **one transaction** (session row + user message + assistant message), and only after the LLM has answered. Failed requests (422 or 503) therefore never leave half a conversation behind.
- The code uses Python's built-in `sqlite3` with parameterised SQL instead of an ORM: there are only a handful of queries and plain SQL is easy to read.

### API contract notes

- The backend exposes exactly three endpoints. FastAPI's automatic `/docs`, `/redoc` and `/openapi.json` pages are switched off.
- `/health` returns two extra fields (`model`, `failure_simulation_enabled`) and answers `503` if the database check fails.
- The history endpoint returns the full stored metadata for assistant messages, which is a superset of the example in the brief.
- Every error is JSON with a `detail` field. An unexpected error returns `500 {"detail": "internal server error"}`; the traceback only goes to the server log.
- `output_tokens` is the completion token count reported by Gemini. On some prompts Gemini 3.x "thinks" briefly before answering, and Google counts and bills those thinking tokens as output, so a one-word answer can occasionally show a larger number.

### Known limitations

- Render's free plan sleeps when idle and its disk is not persistent, so on the live site the history and the cache are reset whenever the service restarts or is redeployed. Locally with Docker the history is kept in the volume.
- `/chat` is public (no login, as the brief requires), so anyone with the URL can use the free API quota.
- One uvicorn worker and no locking: if two requests for the same session arrive at exactly the same time their order isn't guaranteed. The UI never sends a second message before the first reply has arrived.
- All keys must belong to the same provider and model (`LLM_MODEL`).

## 4. Verification

The commands below use bash. On Windows use Git Bash, or replace `curl` with `curl.exe`. Set `BASE` to `http://localhost:8000` or to the live backend URL.

```bash
BASE=http://localhost:8000
curl -s $BASE/health
```

### Failover

```bash
curl -s -X POST $BASE/chat -H "Content-Type: application/json" \
  -H "X-Simulate-Failure: key_1=429" \
  -d '{"session_id":"demo-failover","message":"Name three primary colours."}'
```

Expect `200` with `"key_id":"key_2"` and `"fallback_attempts":1`. `key_1=500`, `key_1=502` and `key_1=503` behave the same way.

```bash
curl -s -i -X POST $BASE/chat -H "Content-Type: application/json" \
  -H "X-Simulate-Failure: *=429" \
  -d '{"session_id":"demo-all-fail","message":"Hello"}'
curl -s -i $BASE/sessions/demo-all-fail/messages
```

Expect `503 {"detail":"all providers unavailable"}`, followed by `404 {"detail":"session not found"}` because nothing was saved.

In the UI, choose a value in **Simulate key failure (demo)** and send a message. The reply shows `Key key_2` and `Fallbacks 1`, or a red "All AI providers are unavailable" message for `*=429`. The selector goes back to "None" after each message.

### Cache hits

```bash
curl -s -X POST $BASE/chat -H "Content-Type: application/json" \
  -d '{"session_id":"demo-cache-a","message":"What is the capital of France?"}'
curl -s -X POST $BASE/chat -H "Content-Type: application/json" \
  -d '{"session_id":"demo-cache-b","message":"What is the capital of France?"}'
```

The first reply is `LIVE_INFERENCE`. The second one (new session, same first message) is `LLM_CACHE` with the identical reply, the same token counts, `"key_id":null`, and a latency of a few milliseconds instead of around a second.

In the UI: send a question, reload the page (which starts a new session) and send the same question again. The badge turns green (`LLM_CACHE`), the text is identical and the latency drops to a few milliseconds.

### Per-message token usage

Every reply in the UI shows `Input tokens` and `Output tokens` for that request only. In a longer conversation the input tokens of each new request grow, because the history is sent to the model again, but each reply still shows only its own request and never a running total. The stored numbers per assistant message can also be checked with:

```bash
curl -s $BASE/sessions/demo-cache-a/messages
```

### Automated tests and smoke test

- `cd backend && python -m pytest` runs 69 tests covering validation, caching, history, multi-turn context, failover, the simulation header, CORS and the error format. They use LiteLLM's own `mock_response`, so no API keys or network are needed, while LiteLLM's real cache and error handling still run.
- `python backend/scripts/smoke_test.py <backend-url>` runs 28 end-to-end checks against a running backend with real keys: health, live vs cache, identical cached reply, faster cache hit, memory across turns, history format, 404, 422 cases, failover with `key_1=429` and `key_1=500`, and `*=429` returning 503 with nothing stored. For example: `python backend/scripts/smoke_test.py http://localhost:8000`.

## 5. Setup Used

- Editor: Visual Studio Code
- AI tools: Claude Code (Anthropic), used for planning, writing code and running the checks
- Machine: Windows 11 with Docker Desktop, GNU Make, Python 3.12 and Node.js 24

## 6. Bonus features

- **Failure simulator in the UI** – a dropdown that sends `X-Simulate-Failure` with the next message, so failover can be shown from the browser without curl.
- **Key and fallback info on every reply** – besides the required metadata, each reply shows which key answered and how many keys failed first, which makes failover visible at a glance.
- **New chat button** – starts a fresh session without reloading the page.
- **Small UI helpers** – a backend status indicator (it also wakes the Render backend as soon as the page opens), example prompts on the empty screen, and a character counter that turns red above the 4000-character limit.
- **System prompt kept per session** – the prompt is stored in the `sessions` table and the field locks after the first reply, so a conversation can't silently switch prompts halfway through.
- **Smoke test script** – `backend/scripts/smoke_test.py` checks the whole API contract against any running backend, local or live, with one command.
- **Docker health check and non-root user** – the frontend container starts only after the backend reports healthy, and the backend container doesn't run as root.
