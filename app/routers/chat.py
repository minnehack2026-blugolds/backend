from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.db import get_db
from app.core.auth import CurrentUser, require_user
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.conversation_read import ConversationRead
from app.schemas.chat import (
    ConversationCreateIn,
    ConversationOut,
    MessageCreateIn,
    MessageOut,
)

router = APIRouter(prefix="/chat", tags=["chat"])


async def _get_conversation_or_403(
    db: AsyncSession, conversation_id: int, user: CurrentUser
) -> Conversation:
    q = select(Conversation).where(Conversation.id == conversation_id)
    conv = (await db.execute(q)).scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if user.id not in (conv.buyer_id, conv.seller_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return conv


@router.post("/conversations", response_model=ConversationOut)
async def create_or_get_conversation(
    payload: ConversationCreateIn,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    # 1) fetch post -> derive seller
    post = (await db.execute(select(Post).where(Post.id == payload.post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    seller_id = getattr(post, "seller_id", None) or getattr(post, "user_id", None) or getattr(post, "owner_id", None)
    if not seller_id:
        raise HTTPException(status_code=500, detail="Post missing seller_id/user_id")

    buyer_id = user.id
    if buyer_id == seller_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # 2) try insert; if unique conflict -> fetch existing
    conv = Conversation(post_id=post.id, buyer_id=buyer_id, seller_id=seller_id)
    db.add(conv)
    try:
        await db.commit()
        await db.refresh(conv)
        return ConversationOut.model_validate(conv)
    except IntegrityError:
        await db.rollback()

        q = select(Conversation).where(
            and_(
                Conversation.post_id == post.id,
                Conversation.buyer_id == buyer_id,
                Conversation.seller_id == seller_id,
            )
        )
        existing = (await db.execute(q)).scalar_one()
        return ConversationOut.model_validate(existing)


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    # base list
    q = (
        select(Conversation)
        .where(or_(Conversation.buyer_id == user.id, Conversation.seller_id == user.id))
        .order_by(desc(Conversation.updated_at))
    )
    conversations = (await db.execute(q)).scalars().all()

    # hackathon-simple “Option 1”: for each conversation, query last message + unread_count
    out: list[ConversationOut] = []
    for conv in conversations:
        # last message
        last_q = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last = (await db.execute(last_q)).scalar_one_or_none()

        # read row
        read_q = select(ConversationRead).where(
            and_(ConversationRead.conversation_id == conv.id, ConversationRead.user_id == user.id)
        )
        read_row = (await db.execute(read_q)).scalar_one_or_none()

        # unread: messages after last_read_message_id AND not sent by me
        unread_q = select(func.count()).select_from(Message).where(
            and_(
                Message.conversation_id == conv.id,
                Message.sender_id != user.id,
            )
        )
        if read_row and read_row.last_read_message_id:
            unread_q = unread_q.where(Message.id > read_row.last_read_message_id)

        unread_count = (await db.execute(unread_q)).scalar_one()

        dto = ConversationOut.model_validate(conv)
        dto.last_message = last.body if last else None
        dto.last_message_at = last.created_at if last else None
        dto.unread_count = int(unread_count)
        out.append(dto)

    return out


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200),
    before_id: int | None = Query(None, ge=1),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    await _get_conversation_or_403(db, conversation_id, user)

    q = select(Message).where(Message.conversation_id == conversation_id)
    if before_id:
        q = q.where(Message.id < before_id)

    q = q.order_by(desc(Message.created_at)).limit(limit)
    rows = (await db.execute(q)).scalars().all()

    # return newest-last for UI convenience
    return list(reversed([MessageOut.model_validate(m) for m in rows]))


@router.post("/conversations/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: int,
    payload: MessageCreateIn,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    conv = await _get_conversation_or_403(db, conversation_id, user)

    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Message body required")

    msg = Message(conversation_id=conv.id, sender_id=user.id, body=body)
    db.add(msg)

    # bump conversation updated_at by touching it (simple)
    conv.updated_at = func.now()  # type: ignore

    await db.commit()
    await db.refresh(msg)
    return MessageOut.model_validate(msg)


@router.post("/conversations/{conversation_id}/read")
async def mark_read(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_user),
):
    await _get_conversation_or_403(db, conversation_id, user)

    # latest message id
    last_id_q = select(Message.id).where(Message.conversation_id == conversation_id).order_by(desc(Message.id)).limit(1)
    last_id = (await db.execute(last_id_q)).scalar_one_or_none()

    if last_id is None:
        return {"ok": True, "last_read_message_id": None}

    # upsert read row
    read_q = select(ConversationRead).where(
        and_(ConversationRead.conversation_id == conversation_id, ConversationRead.user_id == user.id)
    )
    read_row = (await db.execute(read_q)).scalar_one_or_none()

    if not read_row:
        read_row = ConversationRead(conversation_id=conversation_id, user_id=user.id, last_read_message_id=last_id)
        db.add(read_row)
    else:
        read_row.last_read_message_id = last_id

    await db.commit()
    return {"ok": True, "last_read_message_id": last_id}
