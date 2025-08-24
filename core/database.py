# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.base import get_settings
from core.base import Base

settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
def init_database():
    Base.metadata.create_all(bind=engine)
