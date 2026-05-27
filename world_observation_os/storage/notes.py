from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.founder_note import FounderNote


class NoteStore:
    def __init__(self, session: Session):
        self.session = session

    def add(self, data: dict) -> FounderNote:
        row = FounderNote(**data)
        self.session.add(row)
        self.session.flush()
        return row

    def list_recent(self, limit: int = 50) -> list[FounderNote]:
        stmt = select(FounderNote).order_by(FounderNote.created_at.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
