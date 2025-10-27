import asyncio
from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel
from app.core.database import engine
from app.core.config import settings
from app.domain.chat.models import Chat
from app.domain.message.models import Message
from app.domain.user.models import User
from app.domain.document.models import Document, DocumentChunk


config = context.config
fileConfig(config.config_file_name)


target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Modo offline (sin conexión directa a la BD)"""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Modo online (usando el engine de SQLModel)"""
    connectable = engine.sync_engine if hasattr(engine, "sync_engine") else engine

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # detecta cambios en tipos de columnas
        )

        with context.begin_transaction():
            context.run_migrations()

    if connectable.url.get_backend_name().startswith("postgresql+asyncpg"):
        # Si el motor es asíncrono, usar async context
        async def async_main():
            async with engine.begin() as conn:
                await conn.run_sync(do_run_migrations)

        asyncio.run(async_main())
    else:
        # Motor síncrono (por ejemplo, psycopg2)
        with connectable.begin() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
