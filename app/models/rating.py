from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class Rating(Base):
    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 5", name="check_stars_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False
    )

    
    rater_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    
    ratee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Rating score
    stars: Mapped[int] = mapped_column(Integer, nullable=False)

    
    comment: Mapped[str | None] = mapped_column(String(1000))

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        # 1–5 stars
        CheckConstraint("stars >= 1 AND stars <= 5", name="stars_range"),

        #prevent duplicate rating per transaction per user
        UniqueConstraint(
            "transaction_id",
            "rater_id",
            name="unique_rating_per_transaction"
        ),
    )
