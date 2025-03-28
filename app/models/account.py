from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_type = Column(String(255), nullable=False)
    account_number = Column(String(255), unique=True, nullable=False)
    balance = Column(Numeric(10, 2), default=0.00)   
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with user
    user = relationship("User", back_populates="accounts")

    # Relationships with transactions
    sent_transactions = relationship(
        "Transaction", 
        foreign_keys="[Transaction.from_account_id]", 
        back_populates="from_account"
    )
    received_transactions = relationship(
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
            'currency': self.currency,
            'balance': self.balance,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }