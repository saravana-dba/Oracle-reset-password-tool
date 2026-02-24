import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.config import settings
from app.models import CredentialCheckRequest, PasswordResetRequest, PasswordResetResponse
from app.services.oracle import reset_password, verify_credentials
from app.services.verification_tokens import VerificationTokenStore


logging.basicConfig(
    filename="reset_audit.log",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("audit")


limiter = Limiter(key_func=get_remote_address)
verification_store = VerificationTokenStore(ttl_seconds=300)

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


@app.post("/reset-password", response_model=PasswordResetResponse)
@limiter.limit("5/minute")
def handle_reset_password(request: Request, body: PasswordResetRequest):
    ip = request.client.host
    dsn = settings.get_dsn(body.brand)

    try:
        verification_store.consume_token(body.verification_token, body.username)
        message = reset_password(body.username, body.current_password, body.new_password, dsn)
        logger.info("user=%s brand=%s ip=%s status=SUCCESS", body.username, body.brand, ip)
        return PasswordResetResponse(success=True, message=message)

    except ValueError as e:
        logger.warning("user=%s brand=%s ip=%s status=FAILED reason=%s", body.username, body.brand, ip, e)
        return PasswordResetResponse(success=False, message=str(e))


@app.post("/verify-credentials", response_model=PasswordResetResponse)
@limiter.limit("5/minute")
def handle_verify_credentials(request: Request, body: CredentialCheckRequest):
    ip = request.client.host
    dsn = settings.get_dsn(body.brand)

    try:
        message = verify_credentials(body.username, body.current_password, dsn)
        verification_token = verification_store.create_token(body.username)
        logger.info("user=%s brand=%s ip=%s status=VERIFY_SUCCESS", body.username, body.brand, ip)
        return PasswordResetResponse(
            success=True,
            message=message,
            verification_token=verification_token,
        )

    except ValueError as e:
        logger.warning("user=%s brand=%s ip=%s status=VERIFY_FAILED reason=%s", body.username, body.brand, ip, e)
        return PasswordResetResponse(success=False, message=str(e))
