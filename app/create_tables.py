from app import create_app, db
import sqlalchemy as sa
from app.models.user import User
from app.models.transaction import Transaction
from app.models.account import Account


def initialize_database():
    app = create_app()
    
    with app.app_context():
        # Print connection information
        connection_info = db.engine.url
        print(f"Connected to: {connection_info}")
        
        # Print existing tables
        inspector = sa.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Existing tables: {existing_tables}")
        
        # Print models that should create tables
        print(f"Models to create tables for: {db.Model.__subclasses__()}")
        
        # Create all tables
        db.create_all()
        
        # Check tables after creation
        new_tables = inspector.get_table_names()
        print(f"Tables after db.create_all(): {new_tables}")
        
        print("Database tables created successfully!")

if __name__ == '__main__':
    initialize_database()