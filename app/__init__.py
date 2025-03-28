from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "postgresql://postgres:amanda@localhost:5432/byonegaes"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Import and register blueprints
    from app.routes.user import user_bp
    from app.routes.transaction import transaction_bp
    from app.routes.auth import auth_bp
    from app.routes.account import account_bp
    
    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(user_bp)
    
    return app