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

        user = self.repository.find_user_by_email(email)
        if not user:
            return False, {'message': 'Invalid credentials! No email registered'}, 401

        if not verify_password(user.password, password):
            return False, {'message': "Invalid credentials! Password didn't match"}, 401

        token = generate_token(str(user.id))

        return True, {
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': str(user.id)
            }
        }, 200

    def register(self, user_data: dict):
        print("REGISTER STARTED")
        if 'is_admin' in user_data:
            return False, {'message': 'Forbidden: Only admins can set "is_admin" field.'}, 403

        valid, message = validate_required_fields(user_data, ['username', 'email', 'password'])
        if not valid:
            return False, {'message': message}, 400

        if not validate_email(user_data.get('email')):
            return False, {'message': 'Invalid email format!'}, 400
        print("REGISTER STARTED2")
        valid_password, pwd_message = validate_password(user_data.get('password'))
        print("REGISTER STARTED3")
        if not valid_password:
            return False, {'message': pwd_message}, 400
        print("cek existing")
        if self.repository.user_exists(user_data.get('email')):
            return False, {'message': 'User already exists!'}, 409
        print("hashed password")
        hashed_password = hash_password(user_data.get('password'))
        print("CREATING USER")
        success, result = self.repository.create_user(user_data, hashed_password)
        print("RESULT FROM REPO:", success, result)

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
