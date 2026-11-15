"""
Authentication and Role-Based Authorization Service
"""

from flask import session
from models import User, Role, AuditLog
from database import db

def authenticate_user(email, password):
    """Authenticate user against database credentials."""
    user = User.query.filter_by(email=email.strip().lower(), is_active=True).first()
    if not user:
        return None
    if user.check_password(password):
        return user
    return None

def login_user(user, ip_address='127.0.0.1'):
    """Establish authenticated session and log event."""
    session['user'] = user.to_dict()
    session.permanent = True
    
    # Audit log
    try:
        log = AuditLog(
            user_id=user.id,
            action='LOGIN',
            module='Auth',
            details=f"User {user.email} signed in with role {user.role}.",
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

def logout_user():
    """Clear session."""
    user_info = session.get('user')
    if user_info and 'id' in user_info:
        try:
            log = AuditLog(
                user_id=user_info['id'],
                action='LOGOUT',
                module='Auth',
                details=f"User {user_info.get('email')} signed out."
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()
    session.clear()

def get_current_user():
    """Retrieve current session user object."""
    user_data = session.get('user')
    if not user_data:
        return None
    return User.query.get(user_data.get('id'))
