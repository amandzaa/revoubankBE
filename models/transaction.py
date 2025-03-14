class Transaction:
    def __init__(self, id, account_id, transaction_type, amount, description=None, 
                 transaction_date=None, linked_transaction_id=None):
        self.id = id
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.transaction_date = transaction_date
        self.linked_transaction_id = linked_transaction_id
    
    @classmethod
    def from_row(cls, row):
        """Create a Transaction object from a database row."""
        if row is None:
            return None
            
        return cls(
            id=row['id'],
            account_id=row['account_id'],
            transaction_type=row['transaction_type'],
            amount=row['amount'],
            description=row.get('description'),
            transaction_date=row.get('transaction_date'),
            linked_transaction_id=row.get('linked_transaction_id')
        )
    
    def to_dict(self):
        """Convert Transaction object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'transaction_date': self.transaction_date,
            'linked_transaction_id': self.linked_transaction_id
        }
        