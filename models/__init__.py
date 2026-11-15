"""
CourseFlow Models Package
Exports all relational entities for SQLAlchemy ORM and Alembic migrations.
"""

from models.user import User, Role
from models.course import Course, FacultyAssignment, CourseFileSection, CourseDocument
from models.curriculum import (
    UniversityInfo, SchoolInfo, GraduateAttribute, PEO,
    ProgramOutcome, ProgramSpecificOutcome, CourseOutcome, CO_PO_Mapping
)
from models.syllabus import SyllabusModule, SyllabusUnit, SessionPlan, TimetableEntry
from models.student import (
    Student, StudentEnrolment, Assessment, AssessmentComponent,
    StudentMark, AttendanceRecord
)
from models.feedback import StudentFeedback, Intervention, COAttainmentRecord
from models.engineering import (
    ProjectRequirement, ArchitectureDiagram, TestCase,
    ProjectMilestone, ProjectTask, RiskItem, PertEstimation
)
from models.audit import AuditLog

__all__ = [
    'User', 'Role',
    'Course', 'FacultyAssignment', 'CourseFileSection', 'CourseDocument',
    'UniversityInfo', 'SchoolInfo', 'GraduateAttribute', 'PEO',
    'ProgramOutcome', 'ProgramSpecificOutcome', 'CourseOutcome', 'CO_PO_Mapping',
    'SyllabusModule', 'SyllabusUnit', 'SessionPlan', 'TimetableEntry',
    'Student', 'StudentEnrolment', 'Assessment', 'AssessmentComponent',
    'StudentMark', 'AttendanceRecord',
    'StudentFeedback', 'Intervention', 'COAttainmentRecord',
    'ProjectRequirement', 'ArchitectureDiagram', 'TestCase',
    'ProjectMilestone', 'ProjectTask', 'RiskItem', 'PertEstimation',
    'AuditLog'
]
