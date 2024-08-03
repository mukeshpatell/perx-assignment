# db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

# Setup database connection and session
DATABASE_URL = f"postgresql+psycopg2://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.PG_HOST}:{Config.PG_PORT}/{Config.POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
