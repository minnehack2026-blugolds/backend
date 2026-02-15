from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.user import User

COOKIE_NAME = "access_token"

@dataclass
class CurrentUser:
    id: int
    email: str
    name: str

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    user_id = decode_access_token(token)
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    return CurrentUser(id=user.id, email=user.email, name=user.name)

def require_user(user: CurrentUser | None = Depends(get_current_user)) -> CurrentUser:
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
