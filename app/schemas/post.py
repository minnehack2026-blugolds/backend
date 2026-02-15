from pydantic import BaseModel



class PostCreate(BaseModel):
    title: str
    description: str | None = None
    price_cents: int


class PostUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price_cents: int | None = None
    status: str | None = None


class PostOut(BaseModel):
    id: int
    seller_id: int
    title: str
    description: str | None
    price_cents: int
    status: str

    class Config:
        from_attributes = True
