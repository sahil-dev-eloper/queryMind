from hashlib import sha256


def hash_value(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()
