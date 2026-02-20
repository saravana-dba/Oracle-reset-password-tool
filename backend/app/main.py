import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.config import settings
from app.models import PasswordResetRequest, PasswordResetResponse
from app.services.oracle import reset_password

# ---------------------------------------------------------------------------
# Logging — writes to reset_audit.log. Never logs passwords.
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="reset_audit.log",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("audit")

# ---------------------------------------------------------------------------
# App & middleware
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Oracle Password Reset", version="1.0.0")
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"success": False, "message": "Too many requests. Please try again later."},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.post("/reset-password", response_model=PasswordResetResponse)
@limiter.limit("5/minute")
def handle_reset_password(request: Request, body: PasswordResetRequest):
    ip = request.client.host

    try:
        message = reset_password(body.username, body.current_password, body.new_password)
        logger.info("user=%s ip=%s status=SUCCESS", body.username, ip)
        return PasswordResetResponse(success=True, message=message)

    except ValueError as e:
        logger.warning("user=%s ip=%s status=FAILED reason=%s", body.username, ip, e)
        return PasswordResetResponse(success=False, message=str(e))
