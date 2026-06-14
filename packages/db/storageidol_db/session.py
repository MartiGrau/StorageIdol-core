"""
Async SQLAlchemy session factory.

Each service gets a session via `get_session(client_id)`.
The `client_id` is passed to every query to prevent cross-client data access.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseSettings(BaseSettings):
    """Loaded from environment variables."""

    postgres_user: str = "storageidol"
    postgres_password: str = "storageidol"
    postgres_db: str = "storageidol_dev"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache(maxsize=1)
def _get_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache(maxsize=1)
def engine_for(dsn: str | None = None):
    """Create (and cache) an async engine for the given DSN."""
    settings = _get_settings()
    resolved_dsn = dsn or settings.dsn
    return create_async_engine(
        resolved_dsn,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def _session_factory(dsn: str | None = None) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine_for(dsn),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session(
    client_id: str,
    dsn: str | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that yields a session.

    `client_id` is required as a reminder — it must be filtered on in every query.
    In production each client has a separate Postgres instance (different DSN),
    but in tests and local dev a shared instance uses the client_id column.

    Usage:
        async with get_session("retras") as session:
            result = await session.execute(
                select(Contact).where(Contact.client_id == client_id)
            )
    """
    factory = _session_factory(dsn)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
