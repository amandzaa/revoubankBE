from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_bp = Blueprint('user', __name__, url_prefix='/users')
account_bp = Blueprint('account', __name__, url_prefix='/accounts')
transaction_bp = Blueprint('transaction', __name__, url_prefix='/transactions')

# Import routes to register them with blueprints
from . import auth_routes, user_routes, account_routes, transaction_routes

def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(transaction_bp)