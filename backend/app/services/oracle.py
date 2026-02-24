import oracledb

ORA_ERROR_MESSAGES = {
    1017: "Invalid username or current password.",
    28003: "New password does not meet database complexity requirements.",
    28007: "Password cannot be reused.",
}


def reset_password(username: str, current_password: str, new_password: str, dsn: str) -> str:
    """Connect as the user with their current password and change it to the new one.

    Oracle handles the password change natively via the `newpassword` parameter
    during connection. If the current credentials are valid and the new password
    meets Oracle's policies, the password is changed atomically.

    Args:
        username: The Oracle database username.
        current_password: The user's current password.
        new_password: The desired new password.
        dsn: The Oracle DSN connection string for the target database.

    Returns:
        A success message string.

    Raises:
        ValueError: With a user-friendly message if the operation fails.
    """
    try:
        with oracledb.connect(
            user=username,
            password=current_password,
            dsn=dsn,
            newpassword=new_password,
        ):
            pass
        return "Password changed successfully."

    except oracledb.DatabaseError as e:
        error = e.args[0] if e.args else None
        code = getattr(error, "code", None)
        message = ORA_ERROR_MESSAGES.get(code, "An unexpected database error occurred. Please contact the DBA.")
        raise ValueError(message) from e


def verify_credentials(username: str, current_password: str, dsn: str) -> str:
    """Verify the provided Oracle credentials by attempting a connection.

    Args:
        username: The Oracle database username.
        current_password: The user's current password.
        dsn: The Oracle DSN connection string for the target database.

    Returns:
        A success message string.

    Raises:
        ValueError: With a user-friendly message if verification fails.
    """
    try:
        with oracledb.connect(
            user=username,
            password=current_password,
            dsn=dsn,
        ):
            pass
        return "Credentials verified."

    except oracledb.DatabaseError as e:
        error = e.args[0] if e.args else None
        code = getattr(error, "code", None)
        message = ORA_ERROR_MESSAGES.get(code, "An unexpected database error occurred. Please contact the DBA.")
        raise ValueError(message) from e
