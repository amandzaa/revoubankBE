from datetime import datetime
import re
from flask import g, jsonify
from app.repositories.account import AccountRepository
from app.repositories.user import UserRepository
from app.utils.database_session_manager import DatabaseSessionManager, get_db_session, db_session_manager

def check_account_owner(account_id):
    if not account_id:
        return False, jsonify({'message': 'Account ID is required!'}), 400
    
    # Convert account_id to int if it's a string
    try:
        account_id_int = int(account_id) if isinstance(account_id, str) else account_id
    except ValueError:
        return False, jsonify({'message': 'Invalid Account ID format!'}), 400
    
    # Use the session_scope context manager
    db_session_manager = DatabaseSessionManager()
    with db_session_manager.session_scope():
        # Get the current database session
        session = get_db_session()
        
        # Properly initialize the repository with the session
        account_repository = AccountRepository(db=session)
        account = account_repository.find_by_id(account_id_int)
        
        if not account:
            return False, jsonify({'message': 'Account not found!'}), 404
        
        current_user = g.current_user
        
        # Check if user is admin
        if current_user.get('is_admin', False):
            return True, None, None  # Admin users can access any account
        
        # Convert current user ID to int for comparison if needed
        current_user_id = int(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
        
        # Get account user_id
        account_user_id = account.user_id
        
        # Compare IDs
        if account_user_id != current_user_id:
            return False, jsonify({'message': 'Unauthorized access to this account!'}), 403
        
        return True, None, None

def check_user_owner(user_id):
    if not user_id:
        return False, jsonify({'message': 'User ID is required!'}), 400
    
    # Convert user_id to int if it's a string
    try:
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    except ValueError:
        return False, jsonify({'message': 'Invalid User ID format!'}), 400
    
    # Use the session_scope context manager correctly
    db_session_manager = DatabaseSessionManager()
    with db_session_manager.session_scope():
        user_repository = UserRepository()  # Use without passing session
        user = user_repository.find_by_id(user_id_int)
        print(f"Checking user {user_id}")
        
        if not user:
            return False, jsonify({'message': 'User not found!'}), 404
        
        current_user = g.current_user
        
        # Check if user is admin
        if current_user.get('is_admin', False):
            return True, None, None  # Admin users can access any user account
        
        # Convert current user ID to int for comparison if needed
        current_user_id = int(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
        
        # Compare IDs
        if current_user_id != user_id_int:
            return False, jsonify({'message': 'Unauthorized access to this user account!'}), 403
        
        return True, None, None
    
def check_account_owner_by_identifier(identifier, is_account_number=False):
    if not identifier:
        return False, jsonify({'message': 'Account identifier is required!'}), 400
    
    # Use the session_scope context manager
    db_session_manager = DatabaseSessionManager()
    with db_session_manager.session_scope():
        # Get the current database session
        session = get_db_session()
        
        # Properly initialize the repository with the session
        account_repository = AccountRepository(db=session)
        
        # Get the account using the appropriate method
        if is_account_number:
            account = account_repository.find_by_account_number(identifier)
        else:
            # Convert account_id to int if it's a string
            try:
                account_id_int = int(identifier) if isinstance(identifier, str) else identifier
            except ValueError:
                return False, jsonify({'message': 'Invalidxxx Account ID format!'}), 400
            
            account = account_repository.find_by_id(account_id_int)
        
        if not account:
            return False, jsonify({'message': 'Account not found!'}), 404
        
        current_user = g.current_user
        
        # Check if user is admin
        if current_user.get('is_admin', False):
            return True, None, None  # Admin users can access any account
        
        # Convert current user ID to int for comparison if needed
        current_user_id = int(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
        
        # Get account user_id
        account_user_id = account.user_id
        
        # Compare IDs
        if account_user_id != current_user_id:
            return False, jsonify({'message': 'Unauthorized access to this account!'}), 403
        
        return True, None, None
    
def is_account_number_format(identifier: str) -> bool:
    return bool(re.fullmatch(r"ACC-\d+-\d+", identifier))

def is_valid_transaction_number(txn_number: str) -> bool:
    """Validate a transaction number against expected pattern and known prefixes."""
    valid_prefixes = {'DEP', 'WDR', 'TRF', 'PMT', 'REF', 'FEE', 'INT', 'REV'}
    
    # Regex pattern: PREFIX-YYYYMMDD-XXXXXX
    pattern = r'^([A-Z]{3})-(\d{8})-(\d{6})$'
    match = re.match(pattern, txn_number)
    
    if not match:
        return False

    prefix, date_str, sequence = match.groups()
    
    # Check prefix is valid
    if prefix not in valid_prefixes:
        return False

    # Check date part is a valid date
    try:
        datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        return False

    return True