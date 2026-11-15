"""
Curriculum, Syllabus Planning, Outcomes & Attainment Routes
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.course_service import get_all_courses, get_course_by_id
from services.curriculum_service import get_syllabus_modules, get_session_plans, get_course_outcomes, get_copo_matrix
from services.attainment_service import calculate_course_attainment

curriculum_bp = Blueprint('curriculum', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@curriculum_bp.route('/syllabus')
@login_required
def syllabus():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    modules = get_syllabus_modules(course.id) if course else []
    return render_template('syllabus.html', active_page='syllabus', user=user, course=course, modules=modules)

@curriculum_bp.route('/session-planner')
@curriculum_bp.route('/session_planner')
@login_required
def session_planner():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    sessions = get_session_plans(course.id) if course else []
    return render_template('session_planner.html', active_page='session_planner', user=user, course=course, sessions=sessions)

@curriculum_bp.route('/outcomes')
@login_required
def outcomes():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    course_outcomes = get_course_outcomes(course.id) if course else []
    matrix = get_copo_matrix(course.id) if course else {}
    return render_template('outcomes.html', active_page='outcomes', user=user, course=course, outcomes=course_outcomes, matrix=matrix)

@curriculum_bp.route('/attainment')
@login_required
def attainment():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    records = calculate_course_attainment(course.id) if course else []
    course_outcomes = get_course_outcomes(course.id) if course else []
    return render_template('attainment.html', active_page='attainment', user=user, course=course, records=records, outcomes=course_outcomes)
