import hashlib
from typing import Optional

def hash_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hashes the given data string using SHA-256.

    Args:
        data: The string to be hashed.
        salt: Optional salt to append before hashing.

    Returns:
        The hex digest of the hash.
    """
    if salt:
        data += salt
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
