from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User, UserRole


def create_notification(
    db: Session,
    title: str,
    message: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: str | int | None = None,
    action_url: str | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        action_url=action_url,
        read=False,
    )
    db.add(notification)
    return notification


def notify_roles(
    db: Session,
    roles: list[UserRole],
    title: str,
    message: str,
    entity_type: str | None = None,
    entity_id: str | int | None = None,
    action_url: str | None = None,
) -> None:
    recipients = db.scalars(select(User).where(User.role.in_(roles), User.active.is_(True)))
    for recipient in recipients:
        create_notification(db, title, message, recipient.id, entity_type, entity_id, action_url)


def list_user_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    stmt = select(Notification).where(or_(Notification.user_id == user.id, Notification.user_id.is_(None)))
    if unread_only:
        stmt = stmt.where(Notification.read.is_(False))
    return list(db.scalars(stmt.order_by(Notification.read, Notification.created_at.desc(), Notification.id.desc()).limit(100)))


def mark_notification_read(db: Session, notification_id: int, user: User) -> Notification | None:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            or_(Notification.user_id == user.id, Notification.user_id.is_(None)),
        )
    )
    if notification is None:
        return None
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification
