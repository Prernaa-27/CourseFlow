"""
CourseFlow Routes Package
Registers all modular Blueprints with the Flask application.
"""

from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.curriculum_routes import curriculum_bp
from routes.student_routes import student_bp
from routes.engineering_routes import engineering_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(curriculum_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(engineering_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
