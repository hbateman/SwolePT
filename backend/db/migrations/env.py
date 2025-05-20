from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path
from common.env import load_environment

# Add the backend directory to sys.path to allow importing our modules
backend_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(backend_dir))

# Load environment variables from .env file in project root
env_path = backend_dir.parent / '.env'
print(f"Loading .env from: {env_path}")
load_environment()

# Debug: Print environment variables
print("Environment variables:")
print(f"DATABASE_USER: {os.getenv('DATABASE_USER')}")
print(f"DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD')}")
print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST')}")
print(f"DATABASE_PORT: {os.getenv('DATABASE_PORT')}")
print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME')}")

# Import our database models and configuration
from db.models import Base
from db.providers import get_provider

# Get database URL from provider
provider = get_provider()
DATABASE_URL = provider.get_connection_url()
print(f"Database URL: {DATABASE_URL}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with our provider's URL
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 