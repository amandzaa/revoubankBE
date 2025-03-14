class Account:
    def __init__(self, id, user_id, account_type, currency, balance=0.0, 
                 account_name=None, status='active', created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.account_name = account_name
        self.account_type = account_type
        self.currency = currency
        self.balance = balance
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_row(cls, row):
        # Create an Account object from a database row."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            account_name=row.get('account_name'),
            account_type=row['account_type'],
            currency=row['currency'],
            balance=row['balance'],
            status=row.get('status', 'active'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def to_dict(self):
        # Convert Account object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'currency': self.currency,
            'balance': self.balance,
            'status': self.status,
            'created_at': self.created_at
        }
        