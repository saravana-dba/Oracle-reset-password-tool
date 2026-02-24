from typing import Literal

from pydantic import BaseModel, Field

ORACLE_USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9_$#]*$"

BRAND_TYPE = Literal["avis", "budget"]


class PasswordResetRequest(BaseModel):
    brand: BRAND_TYPE
    username: str = Field(min_length=1, max_length=128, pattern=ORACLE_USERNAME_PATTERN)
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    verification_token: str = Field(min_length=1)


class CredentialCheckRequest(BaseModel):
    brand: BRAND_TYPE
    username: str = Field(min_length=1, max_length=128, pattern=ORACLE_USERNAME_PATTERN)
    current_password: str = Field(min_length=1)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
    verification_token: str | None = None
