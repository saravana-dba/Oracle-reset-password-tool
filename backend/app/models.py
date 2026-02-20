from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    username: str = Field(min_length=1)
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
