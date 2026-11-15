"""
CourseFlow Database Module
Instantiates SQLAlchemy ORM instance and database initialization helper.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask application context."""
    db.init_app(app)
    with app.app_context():
        # Ensure uploads folder exists
        import os
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
        # Create all tables if they do not exist
        db.create_all()
