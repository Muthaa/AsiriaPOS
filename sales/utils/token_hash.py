import hashlib
from django.conf import settings


def hash_token(value: str) -> str:
    if not value:
        return ""
    salt = getattr(settings, 'TOKEN_HASH_SALT', '')
    data = (salt + '|' + value).encode('utf-8')
    return hashlib.sha256(data).hexdigest()
