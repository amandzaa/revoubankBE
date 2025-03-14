class User:
    def __init__(self, id, name, email, password, phone=None, is_admin=False, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.is_admin = is_admin
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_row(cls, row):
        """Create a User object from a database row."""
        if row is None:
            return None
            
        return cls(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            password=row['password'],
            phone=row['phone'],
            is_admin=row['is_admin'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def to_dict(self, exclude_password=True):
        """Convert User object to dictionary for JSON serialization."""
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'updated_at': self.updated_at,
            'created_at': self.created_at
        }
        if not exclude_password:
            user_dict['password'] = self.password
        return user_dict
    