# E-Library Management System API

A production-ready, asynchronous FastAPI backend for managing library books, user accounts, borrowing lifecycles, and automated AI-generated book summaries.

**Live API Docs:** [Swagger UI](https://e-library-kt57.onrender.com/docs)

---

## Features

- **Modern FastAPI & Pydantic V2** — type-safe validation, `Annotated` dependency injection, and auto-generated Swagger UI docs with pre-filled examples.
- **Asynchronous PostgreSQL** — SQLAlchemy (AsyncIO) + `asyncpg` for non-blocking database operations.
- **AI-Generated Summaries, Cached** — book summaries are generated once via an LLM and persisted, so repeat requests are served from Postgres instead of re-calling the AI provider.
- **Fail-safe caching** — a failed AI call is never written to the cache; only successful summaries are persisted, so a transient outage can't permanently poison a book's summary.
- **Robust Error Handling** — unique-constraint violations (`IntegrityError`) are caught specifically rather than masked by a broad `except Exception`, so real bugs surface instead of being reported as generic client errors.
- **Inventory Control** — checkout/return is modeled as a simple state machine per `(user, book)` pair via `BorrowRecord.return_date`.

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (SQLAlchemy AsyncIO + `asyncpg`) |
| Validation | Pydantic V2 |
| AI / Network | HTTPX → Userfacet LLM API (`gpt-4o-mini`) |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/books` | Create a book |
| `GET` | `/api/books` | Search/list books |
| `POST` | `/api/users` | Create a user |
| `GET` | `/api/books/{id}/summary` | Get (or generate + cache) an AI summary for a book |
| `POST` | `/api/borrow` | Borrow a book |
| `POST` | `/api/return` | Return a book |

Full request/response schemas are available in the [Swagger UI](https://e-library-kt57.onrender.com/docs).

## Key Design Decisions

- **Why async (`asyncpg` + `AsyncSession`)** — the AI summary call is the slowest part of the request. An async stack lets the event loop keep serving other requests while waiting on that network I/O, instead of blocking a worker thread.
- **Why cache summaries in Postgres, not in-memory/Redis** — survives restarts, shared across app instances, and needs no extra infrastructure for something this simple.
- **Why Pydantic schemas are separate from the ORM models** — decouples the public API contract from internal storage, so a column can be renamed or an internal-only field added without breaking clients or leaking data (e.g. `hashed_password`) that was never meant to be serialized.
- **Why a single `db.commit()` per endpoint** — in `borrow_book`, the new `BorrowRecord` insert and the `available_copies` decrement commit together atomically, so a crash mid-request can't leave a borrow record with no matching inventory change (or vice versa).

## Known Limitations

- **No authentication** — `user_id` is currently trusted from the request body rather than a verified JWT. In a production system this would come from `Depends(get_current_user)`.
- **No row locking on borrow** — a real deployment should guard the last-copy race condition with either `SELECT ... FOR UPDATE` (pessimistic) or a conditional `UPDATE ... WHERE available_copies > 0` + rowcount check (optimistic).
- **No pagination** on `GET /api/books` — fine at current scale, would need `limit`/`offset` or cursor pagination for a larger catalog.
- **`Base.metadata.create_all` instead of Alembic** — convenient for local dev, but a real deployment should use versioned migrations.

## Local Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manas-0/E-Library.git
   cd E-Library
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # macOS / Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```env
   AI_API_TOKEN=your_token_here
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/elibrary
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The interactive docs will be available at `http://127.0.0.1:8000/docs`.

## License

Add a license (e.g. MIT) here if you intend this repo to be publicly reusable.
