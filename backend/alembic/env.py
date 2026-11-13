import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Import all models to register them with Base
import app.models.audit_event  # noqa: F401
import app.models.classification_review  # noqa: F401
import app.models.longlist  # noqa: F401
import app.models.longlist_adjustment  # noqa: F401
import app.models.longlist_proposal  # noqa: F401
import app.models.longlist_ranked_supplier  # noqa: F401
import app.models.need  # noqa: F401
import app.models.need_attributes  # noqa: F401
import app.models.panel_match  # noqa: F401
import app.models.provider_candidate  # noqa: F401
import app.models.supplier_count_validation  # noqa: F401
import app.models.supplier_evidence_item  # noqa: F401
import app.models.tender_dispatch  # noqa: F401
import app.models.user  # noqa: F401
import app.models.vms_handoff  # noqa: F401
from app.database import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment variable
database_url = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
config.set_main_option("sqlalchemy.url", database_url)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
