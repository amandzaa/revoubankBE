from app import db

Base = db.Model

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

# This allows importing models directly from the models package
__all__ = ['Base', 'User', 'Account', 'Transaction']