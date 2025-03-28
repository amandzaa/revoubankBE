from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    to_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(255), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
        """Convert model to dictionary for easy serialization"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'transaction_date': self.transaction_date,
            'linked_transaction_id': self.linked_transaction_id
        }