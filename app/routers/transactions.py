from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.transaction import Transaction
from app.core.auth import require_user, CurrentUser

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("")
async def create_transaction(post_id: int,
                             seller_id: int,
                             db: AsyncSession = Depends(get_db),
                             user: CurrentUser = Depends(require_user)):
    tx = Transaction(
        post_id=post_id,
        buyer_id=user.id,
        seller_id=seller_id,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx
