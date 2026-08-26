"""Canonical password hashing contract for BunsekiChat.

All application components that create or verify passwords must use
this module.

Contract:
    plaintext UTF-8
        -> SHA-256 digest (32 bytes)
        -> bcrypt
"""

from __future__ import annotations

import hashlib

import bcrypt


def safe_password(password: str) -> bytes:
    """Convert a plaintext password to the canonical fixed-length digest."""
    password = password or ""
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Hash a password using the canonical SHA-256 -> bcrypt contract."""
    return bcrypt.hashpw(
        safe_password(password),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password generated with the canonical contract."""
    if not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            safe_password(password),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError, AttributeError):
        return False