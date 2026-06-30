"""AIOS Security Utilities."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from aios.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


def generate_secret_key(length: int = 64) -> str:
    """Generate a cryptographically secure secret key."""
    return secrets.token_hex(length)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"aios_{secrets.token_urlsafe(32)}"


def hash_data(data: str) -> str:
    """Create a SHA-256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Strip control characters except newlines and tabs
    text = "".join(
        char for char in text
        if char == "\n" or char == "\t" or (ord(char) >= 32)
    )
    return text.strip()
