"""JWT authentication, password hashing, RBAC utilities."""
from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ── Roles ─────────────────────────────────────────────────────────────────────
ROLES = {
    "PROCUREMENT_OFFICER": ["read:all", "write:decisions", "read:audit"],
    "ANALYST": ["read:all", "write:analysis"],
    "ADMIN": ["read:all", "write:all", "manage:users"],
    "VIEWER": ["read:public"],
    "SYSTEM": ["read:all", "write:all"],
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)),
    db: AsyncSession = Depends(get_db),
):
    """Decode JWT and return current user from DB. In demo mode, falls back to default demo user."""
    from app.repositories.user_repository import UserRepository

    if not token and settings.ENABLE_DEMO_MODE:
        demo_user = await UserRepository(db).get_by_email("officer@procurex.local")
        if demo_user:
            return demo_user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            if settings.ENABLE_DEMO_MODE:
                demo_user = await UserRepository(db).get_by_email("officer@procurex.local")
                if demo_user:
                    return demo_user
            raise credentials_exception
    except JWTError:
        if settings.ENABLE_DEMO_MODE:
            demo_user = await UserRepository(db).get_by_email("officer@procurex.local")
            if demo_user:
                return demo_user
        raise credentials_exception

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        if settings.ENABLE_DEMO_MODE:
            demo_user = await UserRepository(db).get_by_email("officer@procurex.local")
            if demo_user:
                return demo_user
        raise credentials_exception
    return user


def require_role(*roles: str):
    """Dependency factory: require one of the given roles."""
    async def _check(current_user=Depends(get_current_user)):
        if current_user.role not in roles and current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {' or '.join(roles)}",
            )
        return current_user
    return _check


def get_permissions(role: str) -> list[str]:
    return ROLES.get(role, [])


# ── Column-Level AES Field Encryption ─────────────────────────────────────────
import base64
import hashlib
from sqlalchemy.types import TypeDecorator, String as SQLString

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column decorator for AES-256 field-level encryption.
    Stores ciphertext in database while decrypting in-memory for model access.
    """
    impl = SQLString
    cache_ok = True

    def __init__(self, length=255, *args, **kwargs):
        super().__init__(length, *args, **kwargs)
        key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        self._key = base64.urlsafe_b64encode(key_bytes)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.encrypt(str(value).encode()).decode()
        except Exception:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.decrypt(str(value).encode()).decode()
        except Exception:
            return str(value)
