"""Manual founder observations — long-term intuition asset."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class FounderNote(Base):
    __tablename__ = "founder_notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    related_signal_ids: Mapped[list | None] = mapped_column(JSON)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    resonance_level: Mapped[int | None] = mapped_column(Integer)  # 1-5, optional
    observation_type: Mapped[str | None] = mapped_column(String(64))  # freeform
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
