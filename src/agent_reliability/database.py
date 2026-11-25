import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


database_url = URL.create(
    drivername="postgresql+psycopg",
    username="agent_reliability",
    password=os.getenv("POSTGRES_PASSWORD") or "local_dev_only",
    host="127.0.0.1",
    port=5432,
    database="agent_reliability",
)

engine = create_engine(database_url)
SessionFactory = sessionmaker(bind=engine)
