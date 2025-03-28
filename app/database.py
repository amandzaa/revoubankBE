import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Ensure the directory exists
DB_FOLDER = "database"
os.makedirs(DB_FOLDER, exist_ok=True)

# Define database path
DATABASE_URL = f"sqlite:///{DB_FOLDER}/bankRev.db"

# Create engine with specific SQLite configurations
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Required for SQLite
    poolclass=StaticPool  # Helps with multi-threading in SQLite
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