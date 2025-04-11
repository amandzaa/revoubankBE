import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, validates
from app import db

# Keep the enum for reference in Python code
class TransactionType(enum.Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    INTEREST = "interest"
    REVERSAL = "reversal"

# Transaction model
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    transaction_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    from_account = relationship(
        "Account", 
        foreign_keys=[from_account_id], 
        back_populates="sent_transactions"
    )
    to_account = relationship(
        "Account", 
        foreign_keys=[to_account_id], 
        back_populates="received_transactions"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_number': self.transaction_number,
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }