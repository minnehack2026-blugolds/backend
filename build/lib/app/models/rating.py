from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))

    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ratee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    stars: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(String(1000))
