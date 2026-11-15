"""
CourseFlow - Course File Management System (CFMS)
Modular Application Factory & Entrypoint
Powered by PostgreSQL (Supabase) via SQLAlchemy ORM
"""

import os
from flask import Flask, render_template, session, jsonify
from config import Config
from database import db, init_db
from routes import register_blueprints
from services.ai_service import process_handout_with_gemini

# ==============================================================================
# BACKWARD COMPATIBILITY CONSTANTS (FOR EXISTING TEST SUITES)
# ==============================================================================
DEMO_USERS = {
    "faculty@courseflow.demo": {
        "name": "Dr. Shilpa Mahajan",
        "email": "faculty@courseflow.demo",
        "role": "faculty",
        "department": "Computer Science & Engineering",
        "avatar": "SM"
    },
    "admin@courseflow.demo": {
        "name": "Dr. Shilpa Mahajan",
        "email": "admin@courseflow.demo",
        "role": "admin",
        "department": "Academic Affairs / Dept of CSE",
        "avatar": "SM"
    }
}

DEMO_SYLLABUS = {
    'CSE3005': [
        { "unit": 1, "title": "Introduction to Software Engineering & SDLC", "hours": 8, "outcomes": "CO1", "topics": "Software Crisis, Characteristics, Waterfall, Incremental, Spiral, Agile" },
        { "unit": 2, "title": "Requirement Engineering & Prioritization", "hours": 7, "outcomes": "CO1, CO2", "topics": "Requirement Elicitation, Analysis, MoSCoW Prioritization" },
        { "unit": 3, "title": "Software Design & Architectural Modeling", "hours": 6, "outcomes": "CO1, CO2", "topics": "Modularity, Cohesion, Coupling, UML Use Case, Sequence, DFD Context, L0, L1" },
        { "unit": 4, "title": "Coding Standards, Verification & Testing", "hours": 10, "outcomes": "CO2", "topics": "Verification & Validation, Unit, Integration, System, Regression, Security, PyTest" },
        { "unit": 5, "title": "Software Project Management & Estimation", "hours": 8, "outcomes": "CO3", "topics": "Effort & Cost Estimation, Critical Path Method (CPM), PERT Chart" },
        { "unit": 6, "title": "Software Quality Assurance & Maintenance", "hours": 5, "outcomes": "CO3", "topics": "SQA, Quality Control, Corrective/Adaptive Maintenance, Reverse Engineering" },
        { "unit": 7, "title": "AI-Assisted Software Engineering", "hours": 4, "outcomes": "CO3", "topics": "Human-in-the-Loop Validation, Hallucination Spotting, Vulnerability Scanning, AI-assisted TDD" }
    ],
    'CS301': [
        { "unit": 1, "title": "Software Lifecycle & Process Models", "hours": 8, "outcomes": "CO1", "topics": "Agile Principles, Scrum Framework, Sprints, User Stories, Waterfall, Spiral" },
        { "unit": 2, "title": "Requirements Engineering & Modeling", "hours": 9, "outcomes": "CO2", "topics": "Requirements Elicitation, IEEE 830 SRS, UML Use Case, Activity, Sequence Diagrams" }
    ]
}

def create_app(config_class=Config):
    """Application factory for CourseFlow."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database
    init_db(app)

    # Ensure Database has Initial Seed Records
    with app.app_context():
        from models import User
        if not User.query.filter_by(email='admin@courseflow.demo').first():
            try:
                from seed_data import seed_database
                seed_database(reset=False)
            except Exception as e:
                app.logger.warning(f"Auto-seed encountered non-fatal notice: {e}")

    # Register Blueprints
    register_blueprints(app)

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        user = session.get('user')
        return render_template('403.html', user=user), 403

    @app.errorhandler(404)
    def page_not_found(e):
        user = session.get('user')
        return render_template('404.html', user=user), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        user = session.get('user')
        return render_template('404.html', user=user, error_msg="Internal Server Error"), 500

    return app

# Main Application Instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
