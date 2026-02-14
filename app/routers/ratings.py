from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingOut
from app.core.auth import require_user, CurrentUser

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingOut)
async def create_rating(payload: RatingCreate,
                        db: AsyncSession = Depends(get_db),
                        user: CurrentUser = Depends(require_user)):
    rating = Rating(
        transaction_id=payload.transaction_id,
        rater_id=user.id,
        ratee_id=user.id,  # simplify for now
        stars=payload.stars,
        comment=payload.comment,
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating
