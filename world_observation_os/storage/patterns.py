from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.pain_pattern import PainPattern


class PatternStore:
    def __init__(self, session: Session):
        self.session = session

    def add(self, data: dict) -> PainPattern:
        row = PainPattern(**data)
        self.session.add(row)
        self.session.flush()
        return row

    def update(self, pattern_id: int, data: dict) -> PainPattern:
        row = self.session.get(PainPattern, pattern_id)
        if not row:
            raise ValueError(f"Pattern {pattern_id} not found")
        for key, value in data.items():
            if value is not None:
                setattr(row, key, value)
        row.updated_at = datetime.utcnow()
        self.session.flush()
        return row

    def list_all(self) -> list[PainPattern]:
        stmt = select(PainPattern).order_by(PainPattern.updated_at.desc())
        return list(self.session.execute(stmt).scalars().all())

    def get(self, pattern_id: int) -> PainPattern | None:
        return self.session.get(PainPattern, pattern_id)
