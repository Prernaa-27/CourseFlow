"""
Curriculum, Syllabus Modules, Session Plans & CO-PO Service
"""

from database import db
from models import SyllabusModule, SessionPlan, TimetableEntry, CourseOutcome, CO_PO_Mapping, ProgramOutcome, ProgramSpecificOutcome

def get_syllabus_modules(course_id):
    """Retrieve all 7 modules for course."""
    return SyllabusModule.query.filter_by(course_id=course_id).order_by(SyllabusModule.module_number).all()

def get_session_plans(course_id):
    """Retrieve 48 session plans."""
    return SessionPlan.query.filter_by(course_id=course_id).order_by(SessionPlan.session_number).all()

def get_timetable(course_id):
    """Retrieve weekly timetable."""
    return TimetableEntry.query.filter_by(course_id=course_id).all()

def get_course_outcomes(course_id):
    """Retrieve CO1, CO2, CO3."""
    return CourseOutcome.query.filter_by(course_id=course_id).order_by(CourseOutcome.code).all()

def get_copo_matrix(course_id):
    """
    Construct complete CO-PO matrix dictionary:
    { 'CO1': { 'PO1': 2, 'PO2': 3, ... }, ... }
    """
    outcomes = get_course_outcomes(course_id)
    mappings = CO_PO_Mapping.query.filter_by(course_id=course_id).all()
    
    matrix = {}
    for co in outcomes:
        matrix[co.code] = {}
        for i in range(1, 13):
            matrix[co.code][f"PO{i}"] = ""
        for j in range(1, 5):
            matrix[co.code][f"PSO{j}"] = ""
            
    for m in mappings:
        if m.outcome_code in matrix:
            matrix[m.outcome_code][m.target_code] = m.level if m.level > 0 else ""

    return matrix
