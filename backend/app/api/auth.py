"""Authentication API router."""
from datetime import timedelta
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse, UserUpdate
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Login with username + password. Returns JWT access token.
    Also accepts application/json via OAuth2PasswordRequestForm.
    """
    audit = AuditService(db)
    repo = UserRepository(db)
    request_id = getattr(request.state, "request_id", None)

    user = await repo.get_by_username(form_data.username)
    if not user:
        user = await repo.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        await audit.log(
            AuditAction.LOGIN_FAILED, AuditCategory.AUTH,
            user_email=form_data.username,
            source="AUTH_API",
            request_id=request_id,
            ip_address=request.client.host if request.client else None,
            metadata={"reason": "Invalid credentials"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact administrator.",
        )

    access_token = create_access_token(
        data={"sub": user.id, "role": user.role, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    await repo.update_last_login(user.id)

    await audit.log(
        AuditAction.LOGIN, AuditCategory.AUTH,
        user_id=user.id,
        user_email=user.email,
        user_role=user.role,
        entity_type="USER",
        entity_id=user.id,
        source="AUTH_API",
        request_id=request_id,
        ip_address=request.client.host if request.client else None,
    )

    logger.info("user_login", user_id=user.id, username=user.username, role=user.role)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user account (ADMIN only)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only ADMIN can create users.")

    repo = UserRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    # Check uniqueness
    if await repo.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered.")
    if await repo.get_by_username(payload.username):
        raise HTTPException(status_code=409, detail="Username already taken.")

    new_user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role.value,
        department=payload.department,
        designation=payload.designation,
        employee_id=payload.employee_id,
        is_active=True,
        is_verified=True,
    )
    await repo.create(new_user)

    await audit.log(
        AuditAction.USER_CREATE, AuditCategory.ADMIN,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        entity_type="USER",
        entity_id=new_user.id,
        new_value={"username": new_user.username, "role": new_user.role},
        source="AUTH_API",
        request_id=request_id,
    )

    return new_user
