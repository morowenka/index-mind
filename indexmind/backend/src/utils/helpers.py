import hashlib


def hash_content(content: str) -> str:
    sha256_hash_object = hashlib.sha256(content.encode('utf-8'))
    return sha256_hash_object.hexdigest()
