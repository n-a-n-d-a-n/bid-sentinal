"""Database initialization and session management."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# SQLite does not support pool_size / max_overflow
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}
if not _is_sqlite:
    _engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    _engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yield a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def apply_audit_ledger_db_triggers(conn):
    """Applies DB-level triggers to enforce audit_events table immutability."""
    driver = conn.dialect.name
    if driver == "sqlite":
        await conn.exec_driver_sql("""
            CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_update
            BEFORE UPDATE ON audit_events
            BEGIN
                SELECT RAISE(FAIL, 'Audit ledger table audit_events is append-only. UPDATE operations are forbidden.');
            END;
        """)
        await conn.exec_driver_sql("""
            CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_delete
            BEFORE DELETE ON audit_events
            BEGIN
                SELECT RAISE(FAIL, 'Audit ledger table audit_events is append-only. DELETE operations are forbidden.');
            END;
        """)
    elif driver == "postgresql":
        await conn.exec_driver_sql("""
            CREATE OR REPLACE FUNCTION prevent_audit_tampering()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'Audit ledger table audit_events is append-only. UPDATE and DELETE operations are forbidden.';
            END;
            $$ LANGUAGE plpgsql;

            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_prevent_audit_update') THEN
                    CREATE TRIGGER trg_prevent_audit_update
                    BEFORE UPDATE ON audit_events
                    FOR EACH ROW EXECUTE FUNCTION prevent_audit_tampering();
                END IF;

                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_prevent_audit_delete') THEN
                    CREATE TRIGGER trg_prevent_audit_delete
                    BEFORE DELETE ON audit_events
                    FOR EACH ROW EXECUTE FUNCTION prevent_audit_tampering();
                END IF;
            END $$;
        """)


async def init_db():
    """Create tables (for development). Production uses Alembic."""
    import app.models  # noqa: F401 — import all models to register them
    try:
        async with engine.begin() as conn:
            # Only create if not exists — Alembic owns schema in production
            await conn.run_sync(Base.metadata.create_all)
            await apply_audit_ledger_db_triggers(conn)
    except Exception as exc:
        import structlog
        logger = structlog.get_logger(__name__)
        logger.warning("database_init_skipped_offline", error=str(exc))

