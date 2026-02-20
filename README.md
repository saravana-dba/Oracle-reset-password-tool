# Oracle Password Reset

A simple internal web tool that lets Oracle database users reset their own passwords. No admin credentials are stored — users authenticate with their current password, and Oracle handles the change natively.

## How It Works

1. User submits their username, current password, and new password
2. Backend connects to Oracle as that user using their current credentials
3. Oracle validates the identity and changes the password atomically via the `newpassword` connection parameter
4. Success or failure is returned to the UI

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
│   │   ├── main.py            # FastAPI app, CORS, rate limiter, route, audit logger
│   │   ├── config.py          # Pydantic settings from .env
│   │   ├── models.py          # Request/response schemas
│   │   └── services/
│   │       └── oracle.py      # Oracle connection + password reset logic
│   ├── .env.example
│   └── pyproject.toml
├── frontend/
│   └── index.html
└── plan.md
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

## Security

- **No admin credentials stored** — users authenticate as themselves
- **Rate limiting** — 5 requests per minute per IP on the reset endpoint
- **Audit logging** — all attempts logged to `reset_audit.log` (no passwords logged)
- **HTTPS** — should be handled by a reverse proxy in production
