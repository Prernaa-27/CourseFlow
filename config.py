"""
CourseFlow Configuration Module
Handles database URI (Supabase PostgreSQL / SQLite fallback), session security, and AI keys.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'courseflow-cfms-dev-secret-key-2024')
    
    # Database Configuration:
    # Uses Supabase PostgreSQL when DATABASE_URL is present.
    # Automatically fixes 'postgres://' URI prefix to 'postgresql://' for SQLAlchemy compatibility.
    # Gracefully falls back to local SQLite when DATABASE_URL is not provided.
    RAW_DB_URL = os.environ.get('DATABASE_URL', '')
    if RAW_DB_URL.startswith('postgres://'):
        RAW_DB_URL = RAW_DB_URL.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = RAW_DB_URL if RAW_DB_URL else f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'courseflow.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Upload Folder for Course File Attachments
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg'}

    # Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
