from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.auth import require_user, CurrentUser
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostOut
from typing import Optional
from geopy.distance import geodesic


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
async def list_posts(
    min_price: int | None = None,
    max_price: int | None = None,
    seller_id: int | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_miles: float = 10,
    db: AsyncSession = Depends(get_db),
):
    query = select(Post).where(Post.status == "active")

    if min_price is not None:
        query = query.where(Post.price_cents >= min_price)

    if max_price is not None:
        query = query.where(Post.price_cents <= max_price)

    if seller_id is not None:
        query = query.where(Post.seller_id == seller_id)

    query = query.order_by(Post.created_at.desc())

    result = await db.execute(query)
    posts = result.scalars().all()

    if latitude is not None and longitude is not None:
        def is_nearby(post):
            if post.latitude is None or post.longitude is None:
                return False

            post_location = (post.latitude, post.longitude)
            user_location = (latitude, longitude)

            return geodesic(post_location, user_location).miles <= radius_miles

        posts = [post for post in posts if is_nearby(post)]

    return posts

@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post or post.status != "active" :
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
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.seller_id != user.id:
        raise HTTPException(status_code=403)

    post.status = "deleted"
    await db.commit()

    return {"success": True}
