from sqlalchemy.orm import Session
from app.utils.auth import generate_token, verify_password, hash_password
from app.utils.validator_schemas import validate_email, validate_password, validate_required_fields
from app.repositories.auth import AuthRepository

class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)
    
    def login(self, email: str, password: str):
        if not email or not password:
            return False, {'message': 'Email and password are required!'}, 400
        
        # Find user by email
        user = self.repository.find_user_by_email(email)
        if not user:
            return False, {'message': 'Invalid credentials! No email registered'}, 401
        
        # Verify password (using User object's password attribute)
        if not verify_password(user.password, password):
            return False, {'message': 'Invalid credentials! Password didn\'t match'}, 401
        
        # Generate token
        token = generate_token(str(user.id))
        
        return True, {
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': str(user.id)
            }
        }, 200
        
    def register(self, user_data: dict):
        # Prevent setting is_admin through registration
        if 'is_admin' in user_data:
            return False, {'message': 'Forbidden: Only admins can set "is_admin" field.'}, 403
        
        # Validate required fields
        valid, message = validate_required_fields(user_data, ['name', 'email', 'password'])
        if not valid:
            return False, {'message': message}, 400
        
        # Validate email format
        if not validate_email(user_data.get('email')):
            return False, {'message': 'Invalid email format!'}, 400
        
        # Validate password strength
        valid_password, pwd_message = validate_password(user_data.get('password'))
        if not valid_password:
            return False, {'message': pwd_message}, 400
        
        # Check if user already exists
        if self.repository.user_exists(user_data.get('email')):
            return False, {'message': 'User already exists!'}, 409
        
        # Create new user
        hashed_password = hash_password(user_data.get('password'))
        success, result = self.repository.create_user(user_data, hashed_password)
        
        if success:
            user_info = user_data.copy()
            user_info.pop('password', None)
            return True, {
                'message': 'User registered successfully!', 
                'user_id': result,
                'user_data': user_info
            }, 201
        else:
            return False, {'message': f'Registration failed: {result}'}, 500