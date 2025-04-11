from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
from app import db

class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(255), nullable=False)
    account_number = db.Column(db.String(255), unique=True, nullable=False)
    currency = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationship with user
    user = db.relationship("User", back_populates="accounts")

    # Relationships with transactions
    sent_transactions = db.relationship(
        "Transaction", 
        foreign_keys="[Transaction.from_account_id]", 
        back_populates="from_account"
    )
    received_transactions = db.relationship(
        "Transaction", 
        foreign_keys="[Transaction.to_account_id]", 
        back_populates="to_account"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'account_number': self.account_number,
            'currency': self.currency,
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }