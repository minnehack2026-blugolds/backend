from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.auth import require_user, CurrentUser
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut)
async def create_post(payload: PostCreate,
                      db: AsyncSession = Depends(get_db),
                      user: CurrentUser = Depends(require_user)):
    post = Post(
        seller_id=user.id,
        title=payload.title,
        description=payload.description,
        price_cents=payload.price_cents,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("", response_model=list[PostOut])
async def list_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    return list(result.scalars().all())


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)
    return post


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(post_id: int,
                      payload: PostUpdate,
                      db: AsyncSession = Depends(get_db),
                      user: CurrentUser = Depends(require_user)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    if post.seller_id != user.id:
        raise HTTPException(status_code=403)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}")
async def delete_post(post_id: int,
                      db: AsyncSession = Depends(get_db),
                      user: CurrentUser = Depends(require_user)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)

    if post.seller_id != user.id:
        raise HTTPException(status_code=403)

    await db.delete(post)
    await db.commit()
    return {"success": True}
