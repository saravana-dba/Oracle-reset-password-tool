# Project Context: Oracle Reset Password

## Scope
- This repository is an internal Oracle password reset tool.
- Treat all changes as security-sensitive and long-term maintainable.
- Prefer complete, test-backed fixes over quick patches.

## Project Structure
- `backend/app/main.py`: FastAPI routes, rate limits, and request handling.
- `backend/app/models.py`: Pydantic request and response schemas.
- `backend/app/services/oracle.py`: Oracle connectivity and password reset operations.
- `backend/app/services/verification_tokens.py`: Short-lived in-memory verification token store.
- `backend/tests`: Unit and API tests.
- `frontend/index.html`: Browser UI for verify and reset flow.

## Project Architecture
- Backend: FastAPI app in `backend/app`.
- Frontend: static UI in `frontend/index.html`.
- Core flow:
  1. `POST /verify-credentials` validates Oracle credentials.
  2. Backend returns a short-lived `verification_token`.
  3. `POST /reset-password` consumes that token and changes password.

## Security Requirements
- Never persist plaintext Oracle passwords in frontend state after verification.
- Never log secrets or include credentials in error messages.
- Keep both endpoints rate-limited unless explicitly requested otherwise.
- Keep token flow one-time and short-lived.

## API and Validation Rules
- `/verify-credentials` input: `username`, `current_password`.
- `/reset-password` input: `username`, `new_password`, `verification_token`.
- Preserve strict model validation (non-empty username/password fields, password min length).
- If API contracts change, update backend and frontend in the same task.

## Testing Standard
- Before handoff, run:
  - `source backend/.venv/bin/activate`
  - `pytest -q`
- Add or update tests for:
  - Pydantic model validation
  - API happy path and failure path
  - Oracle service error mapping behavior

## Implementation Style
- Keep modules focused on one responsibility.
- All functions must include concise docstrings.
- No `TODO`, `FIXME`, or placeholder implementations.
- Prefer explicit domain errors over generic exceptions.

## Frontend Expectations
- API base should resolve from current host with backend port `8080`.
- Network and server errors must surface actionable messages.
- Keep verify/reset stages explicit in UI.

## Git Rules
- Use the user's git identity only.
- Never add `Co-Authored-By` trailers.
