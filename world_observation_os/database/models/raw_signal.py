"""Original human-generated content — preserve the world as-is."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class RawSignal(Base):
    __tablename__ = "raw_signals"
    __table_args__ = (
        UniqueConstraint(
            "source_platform", "source_type", "external_id",
            name="uq_raw_signals_source",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_platform: Mapped[str] = mapped_column(String(32), default="reddit", index=True)
    subreddit: Mapped[str | None] = mapped_column(String(128), index=True)
    source_type: Mapped[str] = mapped_column(String(16), index=True)  # post | comment
    external_id: Mapped[str] = mapped_column(String(64), index=True)  # post or comment id
    post_id: Mapped[str | None] = mapped_column(String(64), index=True)
    author: Mapped[str | None] = mapped_column(String(128))
    title: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str | None] = mapped_column(String(16))
    region: Mapped[str | None] = mapped_column(String(64))
    context: Mapped[str | None] = mapped_column(String(256))  # freeform, e.g. "housing"
    emotion: Mapped[str | None] = mapped_column(String(128))  # lightweight hint, not truth
    workaround_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[list | None] = mapped_column(JSON)  # flexible strings
    raw_json: Mapped[dict | None] = mapped_column(JSON)
    # Soft priority for review queue — not an "opportunity score"
    review_priority: Mapped[int] = mapped_column(Integer, default=0, index=True)
