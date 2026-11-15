"""
User & Role Authentication Models
"""

from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # admin, faculty, student
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('User', back_populates='role_rel', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='faculty')  # 'admin' or 'faculty'
    department = db.Column(db.String(100), default='Dept of CSE')
    cabin_office = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(10), default='CF')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    role_rel = db.relationship('Role', back_populates='users')

    # Relationships
    courses_coordinated = db.relationship('Course', back_populates='coordinator_rel', lazy=True, foreign_keys='Course.coordinator_id')
    faculty_assignments = db.relationship('FacultyAssignment', back_populates='faculty_rel', lazy=True)
    audit_logs = db.relationship('AuditLog', back_populates='user_rel', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'department': self.department,
            'cabinOffice': self.cabin_office,
            'avatar': self.avatar
        }
