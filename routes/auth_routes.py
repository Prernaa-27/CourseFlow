"""
Authentication and Role Switching Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from services.auth_service import authenticate_user, login_user, logout_user, get_current_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = authenticate_user(email, password)
        if user:
            login_user(user, ip_address=request.remote_addr or '127.0.0.1')
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for('course.dashboard'))
        else:
            flash("Invalid credentials. Please verify your email and password.", "danger")
            return render_template('login.html', error="Invalid password. Please check your credentials.", email=email)

    # Check if already authenticated
    if session.get('user'):
        return redirect(url_for('course.dashboard'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/switch-role', methods=['POST'])
def switch_role():
    """Demo endpoint to switch role between admin and faculty."""
    data = request.get_json() or {}
    new_role = data.get('role', 'faculty').lower()
    
    # Fetch appropriate user from database
    user = User.query.filter_by(role=new_role).first()
    if user:
        session['user'] = user.to_dict()
    else:
        # Fallback dictionary if not yet seeded
        session['user'] = {
            'id': 1 if new_role == 'admin' else 2,
            'name': 'Dr. Shilpa Mahajan' if new_role == 'admin' else 'Dr. Shilpa Mahajan',
            'email': f'{new_role}@courseflow.demo',
            'role': new_role,
            'department': 'Dept of CSE',
            'avatar': 'SM'
        }
    return jsonify({'success': True, 'role': new_role, 'user': session['user']})

@auth_bp.route('/api/current-user')
def current_user():
    return jsonify(session.get('user') or {'role': 'anonymous'})
