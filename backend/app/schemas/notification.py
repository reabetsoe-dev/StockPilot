from datetime import datetime

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    title: str
    message: str
    entity_type: str | None
    entity_id: str | None
    action_url: str | None
    read: bool
    created_at: datetime
    updated_at: datetime
