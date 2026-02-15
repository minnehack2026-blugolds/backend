from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth import require_user, CurrentUser, COOKIE_NAME
from app.models.user import User
from app.schemas.user import SignupIn, LoginIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_KWARGS = dict(
    httponly=True,
    samesite="lax",
    secure=False,   # local dev
    path="/",
)

@router.post("/signup", response_model=UserOut)
async def signup(payload: SignupIn, response: Response, db: AsyncSession = Depends(get_db)):
    # email unique
    result = await db.execute(select(User).where(User.email == payload.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)

    return user

@router.post("/login", response_model=UserOut)
async def login(payload: LoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)

    return user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False, 
    )
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser = Depends(require_user), db: AsyncSession = Depends(get_db)):
    # Option 1: return CurrentUser -> UserOut compatible fields
    return {"id": user.id, "email": user.email, "name": user.name}
