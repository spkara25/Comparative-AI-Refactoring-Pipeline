import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

def get_database_engine(db_url: str = None) -> Engine:
    """
    Returns a SQLAlchemy Engine.
    Defaults to MYSQL_URL from env, or falls back to a local SQLite database for zero-config setups.
    """
    if db_url:
        return create_engine(db_url)

    mysql_url = os.getenv("DATABASE_URL")
    if mysql_url:
        return create_engine(mysql_url)

    # Seamless fallback for running locally/in tests without a live MySQL instance
    return create_engine("sqlite:///results/research_benchmark.db")