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
else:
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise ValueError(
            "Missing database credentials: set DATABASE_URL OR POSTGRES_PASSWORD in your environment or .env."
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER", "agent_reliability"),
        password=password,
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "agent_reliability"),
    )

engine = create_engine(database_url)
SessionFactory = sessionmaker(bind=engine)
