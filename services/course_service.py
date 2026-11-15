"""
Course and Course File Management Service
Handles 25-section tracking, completion metrics, and course files.
"""

from database import db
from models import Course, CourseFileSection, CourseDocument, AuditLog

def get_all_courses():
    """Retrieve all available courses."""
    return Course.query.order_by(Course.code).all()

def get_course_by_id(course_id):
    """Retrieve course by identifier (e.g. 'CSE2724' or 'CSE3005')."""
    if not course_id:
        course_id = 'CSE2724'
    course = Course.query.filter((Course.id == course_id) | (Course.code == course_id)).first()
    if not course:
        course = Course.query.filter_by(code='CSE2724').first() or Course.query.filter_by(code='CSE3005').first()
    return course

def get_course_file_sections(course_id):
    """Retrieve all 25 sections for a given course."""
    return CourseFileSection.query.filter_by(course_id=course_id).order_by(CourseFileSection.section_number).all()

def update_section_status(course_id, section_number, status, notes=None, user_id=None):
    """Update section status and notes."""
    section = CourseFileSection.query.filter_by(course_id=course_id, section_number=section_number).first()
    if not section:
        return None
    section.status = status
    if notes is not None:
        section.notes = notes
    if user_id:
        section.updated_by_id = user_id
    
    # Audit log
    log = AuditLog(
        user_id=user_id,
        action='UPDATE_SECTION',
        module='Course File',
        details=f"Updated Section {section_number} ({section.title}) to '{status}' for {course_id}."
    )
    db.session.add(log)
    db.session.commit()
    return section

def get_course_summary_metrics(course_id):
    """Calculate dashboard metrics for a course."""
    course = get_course_by_id(course_id)
    if not course:
        return {
            'completion': 0,
            'completedSections': 0,
            'totalSections': 25,
            'pendingSections': 25,
            'studentsCount': 0,
            'attendanceAverage': "0.0%",
            'attainmentStatus': 'Pending'
        }
    
    sections = course.sections
    total_sections = len(sections) if sections else 25
    completed = sum(1 for s in sections if s.status == 'Completed') if sections else 0
    in_progress = sum(1 for s in sections if s.status == 'In Progress') if sections else 0
    needs_review = sum(1 for s in sections if s.status == 'Needs Review') if sections else 0
    pending = total_sections - completed
    
    completion_pct = round((completed / total_sections) * 100) if total_sections else 0
    
    # Attendance average
    students_count = len(course.enrolments)
    attendance_records = [e.student_rel.attendance[0] for e in course.enrolments if e.student_rel and e.student_rel.attendance]
    if attendance_records:
        avg_att = round(sum(r.percentage for r in attendance_records) / len(attendance_records), 1)
        critical_att = sum(1 for r in attendance_records if r.percentage < 75.0)
    else:
        avg_att = 0.0
        critical_att = 0

    return {
        'completion': completion_pct,
        'completedSections': completed,
        'inProgressSections': in_progress,
        'needsReviewSections': needs_review,
        'totalSections': total_sections,
        'pendingSections': pending,
        'studentsCount': students_count,
        'attendanceAverage': f"{avg_att}%",
        'attendanceCriticalCount': critical_att,
        'attainmentStatus': 'Attained (Level 3)' if completion_pct > 70 else 'In Progress'
    }
