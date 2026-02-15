from datetime import datetime
from pydantic import BaseModel


class ConversationCreateIn(BaseModel):
    post_id: int


class MessageCreateIn(BaseModel):
    body: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    post_id: int
    buyer_id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime

    # extra “inbox” fields
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0

    class Config:
        from_attributes = True
