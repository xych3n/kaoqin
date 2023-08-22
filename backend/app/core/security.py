import secrets
from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext


SECRET_KEY = secrets.token_urlsafe(32)


def create_access_token(subject: Any, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    claims = {"sub": str(subject), "exp": expire}
    return jwt.encode(claims, key=SECRET_KEY)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
