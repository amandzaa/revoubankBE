import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:amanda@localhost:5432/byonegaes"

# Create engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    # No SQLite-specific connect_args or poolclass needed for PostgreSQL
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()