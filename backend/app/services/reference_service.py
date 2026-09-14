from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import utc_now


def next_reference(db: Session, model: type, column, prefix: str) -> str:
    year = utc_now().year
    stem = f"{prefix}-{year}-"
    existing = db.scalars(select(column).where(column.like(f"{stem}%"))).all()
    highest = 0
    for value in existing:
        try:
            highest = max(highest, int(str(value).split("-")[-1]))
        except ValueError:
            continue
    return f"{stem}{highest + 1:04d}"
