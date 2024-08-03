# config.py

from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin123")
    PG_HOST: str = os.getenv("PG_HOST", "perx_test_db_container")
    PG_PORT: str = os.getenv("PG_PORT", "5432")
    PGDATA: str = os.getenv("PGDATA", "/var/lib/postgresql/data")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "perx_test_db")