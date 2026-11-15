"""
Student Records, Attendance, and Marks Service
"""

from database import db
from models import Student, StudentEnrolment, AttendanceRecord, StudentMark, Assessment

def get_students_for_course(course_id):
    """Retrieve all students enrolled in course."""
    enrolments = StudentEnrolment.query.filter_by(course_id=course_id).all()
    return [e.student_rel for e in enrolments if e.student_rel]

def get_attendance_records(course_id):
    """Retrieve attendance records with status tags."""
    return AttendanceRecord.query.filter_by(course_id=course_id).all()

def get_marks_records(course_id, assessment_id=None):
    """Retrieve marks records with optional assessment filter."""
    query = StudentMark.query.filter_by(course_id=course_id)
    if assessment_id:
        query = query.filter_by(assessment_id=assessment_id)
    return query.all()

def get_assessments_for_course(course_id):
    """Retrieve assessment breakdown for course."""
    return Assessment.query.filter_by(course_id=course_id).all()
