"""
Course and Course File Views
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from services.course_service import get_all_courses, get_course_by_id, get_course_file_sections, get_course_summary_metrics
from services.curriculum_service import get_syllabus_modules, get_session_plans, get_course_outcomes, get_copo_matrix
from services.student_service import get_students_for_course, get_attendance_records, get_marks_records, get_assessments_for_course
from models import UniversityInfo, SchoolInfo, GraduateAttribute, PEO, ProgramOutcome, ProgramSpecificOutcome, StudentMark, AttendanceRecord
from services.attainment_service import calculate_course_attainment, calculate_program_outcome_attainment

course_bp = Blueprint('course', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@course_bp.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    return redirect(url_for('course.dashboard'))

@course_bp.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user')
    courses = get_all_courses()
    metrics = get_course_summary_metrics('CSE2724')
    return render_template('dashboard.html', active_page='dashboard', user=user, courses=courses, metrics=metrics)

@course_bp.route('/courses')
@login_required
def courses():
    user = session.get('user')
    course_list = get_all_courses()
    return render_template('courses.html', active_page='courses', user=user, courses=course_list)

@course_bp.route('/courses/<course_id>')
@login_required
def course_detail(course_id):
    user = session.get('user')
    course = get_course_by_id(course_id)
    if not course:
        # Fallback to primary CSE2724
        course = get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    metrics = get_course_summary_metrics(course.id) if course else {}
    return render_template('course_detail.html', active_page='courses', user=user, course=course, metrics=metrics)

@course_bp.route('/course-file')
@course_bp.route('/course_file')
@login_required
def course_file():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    sections = get_course_file_sections(course.id) if course else []
    metrics = get_course_summary_metrics(course.id) if course else {}
    return render_template('course_file.html', active_page='course_file', user=user, course=course, sections=sections, metrics=metrics)

@course_bp.route('/course-file/preview')
@course_bp.route('/course_file_preview')
@login_required
def course_file_preview():
    user = session.get('user')
    course_id = request.args.get('course', 'CSE2724')
    course = get_course_by_id(course_id) or get_course_by_id('CSE2724') or get_course_by_id('CSE3005')
    
    # Official university metadata for all 25 sections
    univ = UniversityInfo.query.first()
    school = SchoolInfo.query.first()
    gas = GraduateAttribute.query.order_by(GraduateAttribute.code).all()
    peos = PEO.query.order_by(PEO.code).all()
    pos = ProgramOutcome.query.order_by(ProgramOutcome.code).all()
    psos = ProgramSpecificOutcome.query.order_by(ProgramSpecificOutcome.code).all()
    
    modules = get_syllabus_modules(course.id) if course else []
    sessions = get_session_plans(course.id) if course else []
    outcomes = get_course_outcomes(course.id) if course else []
    copo_matrix = get_copo_matrix(course.id) if course else {}
    students = get_students_for_course(course.id) if course else []
    assessments = get_assessments_for_course(course.id) if course else []
    attendance = get_attendance_records(course.id) if course else []
    sections = get_course_file_sections(course.id) if course else []

    # Authentic student performance summary and grade ledger
    enrolments = course.enrolments if course else []
    total_students = len(enrolments)
    all_scores = []
    short_attendance_count = 0
    grade_distribution = {'O': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'F': 0}
    sample_student_rows = []
    
    marks_by_student = {}
    att_by_student = {}
    if course:
        all_marks = StudentMark.query.filter_by(course_id=course.id).all()
        for m in all_marks:
            if m.student_id not in marks_by_student:
                marks_by_student[m.student_id] = {}
            marks_by_student[m.student_id][m.assessment_id] = m.marks_obtained

        att_by_student = {a.student_id: a.percentage for a in AttendanceRecord.query.filter_by(course_id=course.id).all()}

        ass_list = sorted(assessments, key=lambda x: x.id)
        lab_id = ass_list[0].id if len(ass_list) > 0 else None
        proj_id = ass_list[1].id if len(ass_list) > 1 else None
        see_id = ass_list[2].id if len(ass_list) > 2 else None

        for idx, enr in enumerate(enrolments):
            st = enr.student_rel
            if not st:
                continue
            s_marks = marks_by_student.get(st.id, {})
            lab_score = s_marks.get(lab_id, 0.0) or 0.0
            proj_score = s_marks.get(proj_id, 0.0) or 0.0
            see_score = s_marks.get(see_id, 0.0) or 0.0
            total = round(lab_score + proj_score + see_score, 1)
            all_scores.append(total)
            
            att_pct = att_by_student.get(st.id, 85.0)
            if att_pct < 75.0:
                short_attendance_count += 1
                
            if total >= 90:
                grade = 'O'
            elif total >= 80:
                grade = 'A+'
            elif total >= 70:
                grade = 'A'
            elif total >= 60:
                grade = 'B+'
            elif total >= 50:
                grade = 'B'
            elif total >= 40:
                grade = 'C'
            else:
                grade = 'F'
            grade_distribution[grade] += 1
            
            if idx < 20:  # Top 20 for preview table
                sample_student_rows.append({
                    'roll_no': st.roll_no,
                    'name': st.name,
                    'email': st.email,
                    'section': f"Section {((idx % 7) + 1)}",
                    'lab': lab_score,
                    'proj': proj_score,
                    'see': see_score,
                    'total': total,
                    'attendance': att_pct,
                    'grade': grade
                })

    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    max_score = max(all_scores) if all_scores else 0.0
    min_score = min(all_scores) if all_scores else 0.0
    avg_attendance = round(sum(att_by_student.values()) / len(att_by_student), 1) if att_by_student else 0.0
    passed_count = sum(1 for s in all_scores if s >= 40.0)
    failed_count = total_students - passed_count
    pass_percentage = round((passed_count / total_students) * 100.0, 2) if total_students else 0.0

    co_attainments = calculate_course_attainment(course.id) if course else []
    po_calc = calculate_program_outcome_attainment(course.id) if course else {'mappedOnly': []}
    po_attainments = po_calc.get('mappedOnly', [])

    summary_metrics = {
        'total_students': total_students,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pass_percentage': pass_percentage,
        'avg_score': avg_score,
        'max_score': max_score,
        'min_score': min_score,
        'avg_attendance': avg_attendance,
        'short_attendance_count': short_attendance_count,
        'grade_distribution': grade_distribution,
        'sample_students': sample_student_rows
    }

    return render_template(
        'course_file_preview.html',
        active_page='course_file',
        user=user,
        course=course,
        univ=univ,
        school=school,
        gas=gas,
        peos=peos,
        pos=pos,
        psos=psos,
        modules=modules,
        sessions=sessions,
        outcomes=outcomes,
        copo_matrix=copo_matrix,
        students=students,
        assessments=assessments,
        attendance=attendance,
        sections=sections,
        summary_metrics=summary_metrics,
        co_attainments=co_attainments,
        po_attainments=po_attainments
    )

@course_bp.route('/ai-assistant')
@course_bp.route('/ai_assistant')
@login_required
def ai_assistant():
    user = session.get('user')
    courses = get_all_courses()
    return render_template('ai_assistant.html', active_page='ai_assistant', user=user, courses=courses)
