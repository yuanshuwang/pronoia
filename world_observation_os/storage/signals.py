"""Persistence helpers for raw_signals."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.raw_signal import RawSignal


class SignalStore:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, data: dict) -> tuple[RawSignal, bool]:
        stmt = select(RawSignal).where(
            RawSignal.source_platform == data["source_platform"],
            RawSignal.source_type == data["source_type"],
            RawSignal.external_id == data["external_id"],
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing:
            for key in (
                "title", "content", "upvotes", "comment_count", "url",
                "emotion", "workaround_detected", "tags", "review_priority",
                "context", "raw_json",
            ):
                if key in data and data[key] is not None:
                    setattr(existing, key, data[key])
            existing.fetched_at = datetime.utcnow()
            self.session.flush()
            return existing, False

        row = RawSignal(**data)
        self.session.add(row)
        self.session.flush()
        return row, True

    def list_for_review(self, limit: int = 30, min_priority: int = 0) -> list[RawSignal]:
        stmt = (
            select(RawSignal)
            .where(RawSignal.review_priority >= min_priority)
            .order_by(RawSignal.review_priority.desc(), RawSignal.fetched_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_recent(self, limit: int = 50) -> list[RawSignal]:
        stmt = (
            select(RawSignal)
            .order_by(RawSignal.fetched_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get(self, signal_id: int) -> RawSignal | None:
        return self.session.get(RawSignal, signal_id)
