"""
Database Configuration using SQLAlchemy and SQLite.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_FILE = os.getenv("DATABASE_FILE", "hospital_auditor.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

