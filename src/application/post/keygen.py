import secrets
import string

ALPHABET = string.ascii_lowercase + string.digits
KEY_LENGTH = 8


def generate_unique_key() -> str:
    """Generate a cryptographically random 8-char key from [a-z0-9]."""
    return "".join(secrets.choice(ALPHABET) for _ in range(KEY_LENGTH))
