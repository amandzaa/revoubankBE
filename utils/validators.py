import re
from functools import wraps
from flask import request, jsonify

def validate_email(email):
    """Validate email format."""
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_pattern, email))

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""

def validate_currency(currency):
    """Validate that currency is a valid 3-letter code."""
    return bool(re.match(r"^[A-Z]{3}$", currency))

def validate_amount(amount):
    """Validate that amount is a positive number."""
    try:
        amount_float = float(amount)
        return amount_float > 0
    except (ValueError, TypeError):
        return False

def validate_account_type(account_type):
    """Validate account type against allowed values."""
    valid_types = ['checking', 'savings', 'investment', 'credit']
    return account_type.lower() in valid_types

def validate_transaction_type(transaction_type):
    """Validate transaction type against allowed values."""
    valid_types = ['deposit', 'withdrawal', 'transfer']
    return transaction_type.lower() in valid_types

def validate_required_fields(data, required_fields):
    if not data:
        return False, "No data provided!"
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, ""
