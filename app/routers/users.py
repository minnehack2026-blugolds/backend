from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.rating import Rating
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/average-rating")
async def get_average_rating(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Check user exists
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(
            func.avg(Rating.stars),
            func.count(Rating.id)
        ).where(Rating.ratee_id == user_id)
    )

    avg, count = result.one()

    return {
        "user_id": user_id,
        "average_rating": round(float(avg), 2) if avg is not None else 0,
        "rating_count": count,
    }
