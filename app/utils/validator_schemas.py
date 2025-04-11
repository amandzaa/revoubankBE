import re
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

from app.models.transaction import TransactionType

# ✅ Standalone validation functions (to fix import issues)
def validate_email(email: str) -> str:
    """Validates email format."""
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email

def validate_password(password: str):
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    return True, "Password is valid"

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

def validate_account_type(account_type):
    """Validate account type against allowed values."""
    valid_types = ['checking', 'savings', 'investment', 'deposit']
    return account_type.lower() in valid_types

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

def validate_transaction_type(transaction_type):
    """Validate transaction type against allowed values."""
    valid_types = [t.value for t in TransactionType]
    return transaction_type.lower() in valid_types

# ✅ User Schema
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr

    @validator("email")
    def email_validator(cls, email):
        return validate_email(email)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator("password")
    def password_validator(cls, password):
        return validate_password(password)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

    @validator("email", always=True, pre=True)
    def email_validator(cls, email):
        if email is not None:
            return validate_email(email)
        return email

    @validator("password", always=True, pre=True)
    def password_validator(cls, password):
        if password is not None:
            return validate_password(password)
        return password

# ✅ Account Schema
class AccountBase(BaseModel):
    user_id: int
    account_type: str
    currency: str

    @validator("account_type")
    def account_type_validator(cls, account_type):
        return validate_account_type(account_type)

    @validator("currency")
    def currency_validator(cls, currency):
        return validate_currency(currency)

class AccountCreate(AccountBase):
    initial_balance: float = Field(..., gt=0)

class AccountResponse(AccountBase):
    id: int
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # ✅ Pydantic v2 fix

class AccountUpdate(BaseModel):
    account_type: Optional[str] = None
    currency: Optional[str] = None

    @validator("account_type", always=True, pre=True)
    def account_type_validator(cls, account_type):
        return validate_account_type(account_type)

    @validator("currency", always=True, pre=True)
    def currency_validator(cls, currency):
        return validate_currency(currency)

# ✅ Transaction Schema
class TransactionBase(BaseModel):
    account_id: int
    amount: float
    transaction_type: str
    currency: str
    description: Optional[str] = None

    @validator("amount")
    def ammount_validator(cls, amount):
        return validate_amount(amount)

    @validator("transaction_type")
    def transaction_type_validator(cls, transaction_type):
        return validate_transaction_type(transaction_type)

    @validator("currency")
    def currency_validator(cls, currency):
        return validate_currency(currency)

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 fix
