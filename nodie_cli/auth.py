"""
Secure credential storage using system keyring.
"""

import json
from typing import Optional, Tuple

import keyring

SERVICE_NAME = "nodie-cli"
USERNAME_KEY = "nodie_user"


def save_credentials(email: str, token: str, user_id: str) -> None:
    """Save credentials securely using system keyring."""
    credentials = {
        "email": email,
        "token": token,
        "user_id": user_id,
    }
    keyring.set_password(SERVICE_NAME, USERNAME_KEY, json.dumps(credentials))


def get_credentials() -> Optional[dict]:
    """Get saved credentials from system keyring."""
    try:
        data = keyring.get_password(SERVICE_NAME, USERNAME_KEY)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


def get_token() -> Optional[str]:
    """Get the saved authentication token."""
    creds = get_credentials()
    if creds:
        return creds.get("token")
    return None


def get_user_info() -> Optional[Tuple[str, str]]:
    """Get saved user email and ID."""
    creds = get_credentials()
    if creds:
        return creds.get("email"), creds.get("user_id")
    return None, None


def clear_credentials() -> None:
    """Clear saved credentials."""
    try:
        keyring.delete_password(SERVICE_NAME, USERNAME_KEY)
    except keyring.errors.PasswordDeleteError:
        pass
