from pydantic import BaseModel


class RatingCreate(BaseModel):
    transaction_id: int
    stars: int
    comment: str | None = None


class RatingOut(BaseModel):
    id: int
    transaction_id: int
    stars: int
    comment: str | None

    class Config:
        from_attributes = True
