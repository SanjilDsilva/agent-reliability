import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


raw_url = os.getenv("DATABASE_URL")

if raw_url:
    database_url = raw_url
elif os.getenv("POSTGRES_PASSWORD"):
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER", "agent_reliability"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "agent_reliability"),
    )
else:
    # Zero-config embedded database for standalone cloud platforms like Hugging Face Spaces
    database_url = "sqlite:///./agent_reliability.db"

engine = create_engine(database_url)
SessionFactory = sessionmaker(bind=engine)
