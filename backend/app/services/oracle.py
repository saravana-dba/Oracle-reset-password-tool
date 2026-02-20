import oracledb

from app.config import settings

# Map Oracle error codes to user-friendly messages.
ORA_ERROR_MESSAGES = {
    1017: "Invalid username or current password.",
    28003: "New password does not meet database complexity requirements.",
    28007: "Password cannot be reused.",
}


def reset_password(username: str, current_password: str, new_password: str) -> str:
    """Connect as the user with their current password and change it to the new one.

    Oracle handles the password change natively via the `newpassword` parameter
    during connection. If the current credentials are valid and the new password
    meets Oracle's policies, the password is changed atomically.

    Returns a success message or raises a ValueError with a user-friendly error.
    """
    try:
        with oracledb.connect(
            user=username,
            password=current_password,
            dsn=settings.oracle_dsn,
            newpassword=new_password,
        ):
            pass
        return "Password changed successfully."

    except oracledb.DatabaseError as e:
        error = e.args[0] if e.args else None
        code = getattr(error, "code", None)
        message = ORA_ERROR_MESSAGES.get(code, "An unexpected database error occurred. Please contact the DBA.")
        raise ValueError(message) from e
