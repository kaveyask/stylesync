"""
auth.py
Minimal password hashing helpers, stdlib only (no extra dependency like
bcrypt needed). Uses PBKDF2-HMAC-SHA256 with a random per-user salt.
"""

import hashlib
import os
import re

PBKDF2_ITERATIONS = 100_000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(EMAIL_RE.match(email.strip()))


def hash_password(password, salt=None):
    """Returns (hash_hex, salt_hex). Generates a new salt if none is given."""
    if salt is None:
        salt_bytes = os.urandom(16)
    else:
        salt_bytes = bytes.fromhex(salt)

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt_bytes, PBKDF2_ITERATIONS
    )
    return hash_bytes.hex(), salt_bytes.hex()


def verify_password(password, salt_hex, expected_hash_hex):
    computed_hash, _ = hash_password(password, salt=salt_hex)
    return computed_hash == expected_hash_hex
