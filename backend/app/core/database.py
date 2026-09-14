from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

LOCAL_SQLITE_PREFIXES = ("sqlite://", "sqlite:///")


class Base(DeclarativeBase):
    pass


def build_database_url() -> str:
    configured_url = settings.database_url.strip() or "sqlite:///./stockpilot.db"
    if settings.turso_database_url and (
        configured_url == "sqlite:///./stockpilot.db" or configured_url.startswith("libsql://")
    ):
        turso_url = settings.turso_database_url.strip()
        if turso_url.startswith("sqlite+libsql://"):
            return turso_url
        separator = "&" if "?" in turso_url else "?"
        return f"sqlite+{turso_url}{separator}secure=true"

    if configured_url.startswith("libsql://"):
        separator = "&" if "?" in configured_url else "?"
        return f"sqlite+{configured_url}{separator}secure=true"

    if settings.running_on_vercel and configured_url == "sqlite:///./stockpilot.db":
        return "sqlite:////tmp/stockpilot.db"

    return configured_url


DATABASE_URL = build_database_url()


def build_connect_args(database_url: str) -> dict[str, str | bool]:
    if database_url.startswith("sqlite+libsql://"):
        if settings.turso_auth_token:
            return {"auth_token": settings.turso_auth_token}
        return {}
    if database_url.startswith(LOCAL_SQLITE_PREFIXES):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    DATABASE_URL,
    connect_args=build_connect_args(DATABASE_URL),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
