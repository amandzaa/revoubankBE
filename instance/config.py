# Configuration settings for different environments
import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'revobank.db')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_revobank.db')

class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # In production, ensure SECRET_KEY is set in environment variables

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
