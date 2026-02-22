# Oracle Password Reset

A simple internal web tool that lets Oracle database users reset their own passwords. No admin credentials are stored — users authenticate with their current password, and Oracle handles the change natively.

## How It Works

1. User enters their username and current password
2. Backend connects to Oracle to verify the credentials and returns a short-lived verification token (5-minute TTL)
3. User enters their new password
4. Backend validates the token, then connects to Oracle with the current and new passwords to change it atomically via the `newpassword` connection parameter
5. Success or failure is returned to the UI

## Tech Stack

- **Backend:** Python, FastAPI, oracledb (thin mode), slowapi
- **Frontend:** Plain HTML, Tailwind CSS, vanilla JS
- **Database:** Oracle 19c
- **Package Manager:** uv

## Project Structure

```
oracle_resetpass/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, rate limiter, routes, audit logger
│   │   ├── config.py          # Pydantic settings from .env
│   │   ├── models.py          # Request/response schemas
│   │   └── services/
│   │       ├── oracle.py      # Oracle connection + password reset logic
│   │       └── verification_tokens.py  # In-memory one-time verification token store
│   ├── tests/
│   │   ├── conftest.py        # Shared fixtures (test client, Oracle mocks, token mocks)
│   │   ├── test_api.py        # API endpoint tests
│   │   ├── test_models.py     # Pydantic model validation tests
│   │   └── test_oracle_service.py  # Oracle service unit tests
│   ├── .env.example
│   └── pyproject.toml
├── frontend/
│   └── index.html
└── README.md
```

## Setup

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your Oracle DSN
uv sync
uv run uvicorn app.main:app --reload --port 8080
```

The API will be available at `http://localhost:8080`.

### Frontend

Serve the frontend from the `frontend/` directory:

```bash
cd frontend
python3 -m http.server 5500
```

Then open `http://localhost:5500` in your browser.

## Configuration

Create a `.env` file in `backend/` with:

```
ORACLE_DSN=host:port/service_name
CORS_ORIGINS=["http://localhost:5500"]
```

## Testing

```bash
cd backend
uv run pytest tests/ -v
```

## Security

- **No admin credentials stored** — users authenticate as themselves
- **No server-side password storage** — verification tokens map to usernames only; the current password is re-sent from the frontend on the reset request and never held in server memory
- **Username validation** — usernames are validated against Oracle identifier rules (`^[a-zA-Z][a-zA-Z0-9_$#]*$`, max 128 chars) before reaching the database
- **One-time verification tokens** — tokens are consumed on use and expire after 5 minutes
- **Rate limiting** — 5 requests per minute per IP on both endpoints
- **Audit logging** — all attempts logged to `reset_audit.log` (no passwords logged)
- **HTTPS** — must be handled by a reverse proxy (e.g. nginx with TLS) in production
