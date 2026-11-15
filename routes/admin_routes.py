"""
Administrative Management Routes (Strictly Restricted to 'admin' Role)
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from services.course_service import get_all_courses
from models import User, Course, FacultyAssignment

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/faculty')
@admin_required
def faculty():
    user = session.get('user')
    faculty_list = User.query.filter_by(role='faculty').all()
    courses = get_all_courses()
    return render_template('admin_faculty.html', active_page='admin_faculty', user=user, faculty_list=faculty_list, courses=courses)

@admin_bp.route('/courses')
@admin_required
def courses():
    user = session.get('user')
    course_list = get_all_courses()
    return render_template('admin_courses.html', active_page='admin_courses', user=user, courses=course_list)

@admin_bp.route('/assignments')
@admin_required
def assignments():
    user = session.get('user')
    assignments_list = FacultyAssignment.query.all()
    courses = get_all_courses()
    faculty_list = User.query.filter_by(role='faculty').all()
    return render_template('admin_assignments.html', active_page='admin_assignments', user=user, assignments=assignments_list, courses=courses, faculty_list=faculty_list)

@admin_bp.route('/monitoring')
@admin_required
def monitoring():
    user = session.get('user')
    courses = get_all_courses()
    return render_template('admin_monitoring.html', active_page='admin_monitoring', user=user, courses=courses)
