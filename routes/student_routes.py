"""
Academic Records, Students, Marks, Attendance & Feedback Routes
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.course_service import get_all_courses, get_course_by_id
from services.student_service import get_students_for_course, get_attendance_records, get_marks_records, get_assessments_for_course
from models import StudentFeedback, Intervention

student_bp = Blueprint('academic', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/students')
@login_required
def students():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    student_list = get_students_for_course(course.id) if course else []
    return render_template('students.html', active_page='students', user=user, course=course, students=student_list)

@student_bp.route('/assessments')
@login_required
def assessments():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    assessment_list = get_assessments_for_course(course.id) if course else []
    return render_template('assessments.html', active_page='assessments', user=user, course=course, assessments=assessment_list)

@student_bp.route('/marks')
@login_required
def marks():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    marks_list = get_marks_records(course.id) if course else []
    assessment_list = get_assessments_for_course(course.id) if course else []
    students = get_students_for_course(course.id) if course else []
    return render_template('marks.html', active_page='marks', user=user, course=course, marks=marks_list, assessments=assessment_list, students=students)

@student_bp.route('/attendance')
@login_required
def attendance():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    records = get_attendance_records(course.id) if course else []
    return render_template('attendance.html', active_page='attendance', user=user, course=course, attendance=records)

@student_bp.route('/feedback')
@login_required
def feedback():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    feedback_entries = StudentFeedback.query.filter_by(course_id=course.id).all() if course else []
    interventions = Intervention.query.filter_by(course_id=course.id).all() if course else []
    return render_template('feedback.html', active_page='feedback', user=user, course=course, feedbacks=feedback_entries, interventions=interventions)
