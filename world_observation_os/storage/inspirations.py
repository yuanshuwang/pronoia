from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.product_inspiration import ProductInspiration


class InspirationStore:
    def __init__(self, session: Session):
        self.session = session

    def add(self, data: dict) -> ProductInspiration:
        row = ProductInspiration(**data)
        self.session.add(row)
        self.session.flush()
        return row

    def list_recent(self, limit: int = 30) -> list[ProductInspiration]:
        stmt = (
            select(ProductInspiration)
            .order_by(ProductInspiration.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())
