import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./recruitment.db")

engine = create_engine(
    DATABASE_URL,
    # Neon (and most serverless Postgres) closes idle connections; without
    # pre_ping, SQLAlchemy hands out dead connections and every request after
    # a quiet period 500s. pre_ping checks and transparently reconnects.
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
