import os
from datetime import timedelta

# Application configuration
SECRET_KEY = str(os.environ.get('SECRET_KEY', 'dev_secret_key'))
DATABASE = os.path.join('database', 'bankRev.db')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
TESTING = False
PORT = int(os.environ.get('PORT', 5000))

print("DEBUG: Loaded SECRET_KEY =", repr(SECRET_KEY))

# JWT configuration
JWT_EXPIRATION_DAYS = timedelta(days=int(os.environ.get('JWT_EXPIRATION_DAYS', 1)))
