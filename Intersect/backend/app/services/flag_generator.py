import hashlib
import secrets

FLAG_PREFIX = "CTF"


def generate_flag(challenge_slug: str, user_id: str) -> str:
    """
    Generates a unique, unguessable flag for a given (challenge, user) pair.
    Using a random component (not just a hash of user+challenge) means a
    leaked flag can't be reverse-engineered to guess other users' flags.
    """
    random_part = secrets.token_hex(12)
    checksum = hashlib.sha256(f"{challenge_slug}:{user_id}:{random_part}".encode()).hexdigest()[:6]
    return f"{FLAG_PREFIX}{{{challenge_slug}_{random_part}_{checksum}}}"
