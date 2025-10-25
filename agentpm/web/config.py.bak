import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Frontend configuration
    USE_DEV_TEMPLATE = False
    VITE_DEV_SERVER_URL = 'http://localhost:3000'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    USE_DEV_TEMPLATE = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    USE_DEV_TEMPLATE = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    USE_DEV_TEMPLATE = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
