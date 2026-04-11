from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from auth.security import hash_password, verify_password, create_access_token
from auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse


async def register_user(db: AsyncSession, req: RegisterRequest) -> UserResponse | None:
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        return None  # duplicate

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        auth_provider="email",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def login_user(db: AsyncSession, req: LoginRequest) -> TokenResponse | None:
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        return None

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)