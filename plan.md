# Oracle Password Reset Tool — V1 Plan

## Overview
A simple internal web tool that lets Oracle database users reset their own passwords.
No admin credentials are stored — the user authenticates by connecting with their current password,
and Oracle handles the password change natively via the `newpassword` connection parameter.

## Architecture

```
Browser (UI)                Python Backend              Oracle DB (19c)
┌──────────────┐           ┌──────────────┐           ┌──────────┐
│ username     │  POST     │ Receives     │           │          │
│ old password │ ───────►  │ credentials  │ ───────►  │ password │
│ new password │           │ Connects     │           │ changed  │
└──────────────┘           │ via oracledb │           └──────────┘
                           │ (thin mode)  │
                           └──────────────┘
```

## Confirmed Decisions
- **Backend**: Python, FastAPI, oracledb (sync, thin mode), pydantic, python-dotenv, slowapi
- **Package manager**: uv (fast Python package manager, replaces pip + requirements.txt)
- **Frontend**: Plain HTML + Tailwind CDN + vanilla JS (no build step)
- **Oracle**: Version 19c — thin mode confirmed (no Instant Client needed)
- **Sync mode**: No async for V1 — requests are short-lived, low concurrency
- **Network**: Internal (uncle's company network)
- **HTTPS**: Deferred — deployment team will handle TLS/reverse proxy
- **CORS**: Permissive for internal use

## Directory Structure

```
oracle_resetpass/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, rate limiter, routes
│   │   ├── config.py        # Settings from .env via pydantic
│   │   ├── services/
│   │   │   └── oracle.py    # Connection + password reset logic
│   │   └── models.py        # Pydantic request/response schemas
│   ├── .env.example          # Template for environment variables
│   └── pyproject.toml        # Dependencies managed by uv
├── frontend/
│   └── index.html            # Single-file UI (HTML + Tailwind CDN + vanilla JS)
└── plan.md
```

## Phase 1: Backend Structure & Configuration
- [ ] Set up FastAPI project with the directory structure above
- [ ] Use python-dotenv to load ORACLE_DSN and CORS_ORIGINS from .env
- [ ] Implement rate limiting with slowapi — 5 requests/min per IP on /reset-password
- [ ] Set up Python logger writing to reset_audit.log
  - Logs: username, IP address, success/failure status
  - **Never logs passwords**

## Phase 2: Oracle Service & Error Handling
- [ ] Create service function: reset_password(username, current_password, new_password)
- [ ] Use oracledb.connect() with newpassword=new_password parameter
  - Oracle handles the password change during authentication natively
- [ ] Map Oracle error codes to user-friendly messages:
  - ORA-01017 → "Invalid username or current password."
  - ORA-28003 → "New password does not meet database complexity requirements."
  - ORA-28007 → "Password cannot be reused."
  - Catch-all → "An unexpected database error occurred. Please contact the DBA."

## Phase 3: Frontend
- [ ] Single index.html with Tailwind CDN
- [ ] Clean, centered "Password Reset" card UI
- [ ] Form fields: Username, Current Password, New Password, Confirm New Password
- [ ] Client-side validation:
  - New Password and Confirm New Password must match
  - New password minimum 8 characters
- [ ] POST via fetch() to FastAPI backend
- [ ] Loading state: disable submit button + spinner during request
- [ ] Display success/error messages from the API

## Security
- No admin credentials stored — user authenticates as themselves
- Rate limiting to prevent brute force
- Audit logging for accountability
- HTTPS handled at deployment (reverse proxy)

## Environment Variables (.env)
```
ORACLE_DSN=host:port/service_name
CORS_ORIGINS=http://localhost:3000
```
