from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    username: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    verification_token: str = Field(min_length=1)


class CredentialCheckRequest(BaseModel):
    username: str = Field(min_length=1)
    current_password: str = Field(min_length=1)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
    verification_token: str | None = None
