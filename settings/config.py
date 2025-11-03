import os
from pathlib import Path

# Base directory of project
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    # Flask settings
    SECRET_KEY = 'supersecretkey'  # Change this in production!
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'biblioteca.db'}"
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / "uploads"

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'test_biblioteca.db'}"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Override these in instance/config.py
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)

# Export configs
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}