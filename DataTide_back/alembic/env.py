# alembic/env.py
import sys
# 실행 시점에 프로젝트 루트를 자동으로 경로에 포함
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from logging.config import fileConfig

from alembic import context

# Import your app's Base and engine
     #Import 절대경로로 수정
from DataTide_back.core.database import Base, engine
from DataTide_back.models.item import Item
from DataTide_back.models.item_retail import ItemRetail
from DataTide_back.models.location import Location
from DataTide_back.models.ground_weather import GroundWeather
from DataTide_back.models.sea_weather import SeaWeather


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata from your app's Base
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
