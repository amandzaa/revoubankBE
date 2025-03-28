from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

class DatabaseSessionManager:
    def __init__(self, app: Flask = None):
        self.engine = None
        self.SessionLocal = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        # Get database connection string from app configuration
        database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not database_uri:
            raise ValueError("SQLALCHEMY_DATABASE_URI must be set in app configuration")
        
        # Create engine
        self.engine = create_engine(database_uri)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Register teardown handler
        app.teardown_appcontext(self.teardown_session)
    
    def get_session(self) -> Session:
        """Get or create a database session."""
        if not hasattr(g, 'db_session'):
            if self.SessionLocal is None:
                raise RuntimeError("Database session not initialized. Call init_app first.")
            g.db_session = self.SessionLocal()
        return g.db_session
    
    def teardown_session(self, exception=None):
        """Close the database session."""
        db_session = g.pop('db_session', None)
        if db_session is not None:
            db_session.close()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

# Create a global instance
db_session_manager = DatabaseSessionManager()

# Utility function to get current session
def get_db_session() -> Session:
    return db_session_manager.get_session()