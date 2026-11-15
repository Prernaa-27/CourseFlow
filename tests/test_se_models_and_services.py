"""
Automated PyTest Suite for Software Engineering Capstone:
Tests Database Models, 25-Section Course File, Calculations, MoSCoW, QA & SPM.
"""

import pytest
from app import create_app
from config import TestConfig
from database import db
from models import (
    User, Role, Course, CourseFileSection, CourseOutcome, CO_PO_Mapping,
    SyllabusModule, SessionPlan, Student, StudentMark, AttendanceRecord,
    ProjectRequirement, ArchitectureDiagram, TestCase, ProjectMilestone,
    ProjectTask, RiskItem, PertEstimation
)
from services.course_service import get_all_courses, get_course_by_id, update_section_status, get_course_summary_metrics
from services.curriculum_service import get_syllabus_modules, get_session_plans, get_course_outcomes, get_copo_matrix
from services.student_service import get_students_for_course, get_attendance_records, get_marks_records
from services.attainment_service import calculate_course_attainment
from services.se_service import get_requirements, get_architecture_diagrams, get_test_management_data, get_spm_dashboard_data
from seed_data import seed_database

@pytest.fixture(scope='module')
def test_app():
    """Create test application with in-memory SQLite database."""
    app = create_app(TestConfig)
    with app.app_context():
        # Seed test database directly into the app's database connection
        seed_database(reset=True, app=app)
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

# ==============================================================================
# 1. DATABASE & RELATIONSHIP TESTS
# ==============================================================================
def test_cse3005_course_persisted(test_app):
    with test_app.app_context():
        course = Course.query.filter_by(code='CSE3005').first()
        assert course is not None
        assert course.title == 'Software Engineering'
        assert course.credits == 3
        assert course.academic_year == '2026-27'
        assert course.batch == 'Batch 2024'
        assert course.coordinator_rel is not None
        assert 'Dr. Shilpa Mahajan' in course.coordinator_rel.name

def test_course_file_25_sections_exist(test_app):
    with test_app.app_context():
        sections = CourseFileSection.query.filter_by(course_id='CSE3005').order_by(CourseFileSection.section_number).all()
        assert len(sections) == 25
        assert sections[0].section_number == 1
        assert "Course Details" in sections[0].title
        assert sections[24].section_number == 25
        assert "Additional Information" in sections[24].title

def test_update_section_status_workflow(test_app):
    with test_app.app_context():
        sec = update_section_status('CSE3005', 23, 'Completed', notes='Minutes signed by HOD')
        assert sec is not None
        assert sec.status == 'Completed'
        assert sec.notes == 'Minutes signed by HOD'
        
        # Verify persistence in database
        refreshed = CourseFileSection.query.filter_by(course_id='CSE3005', section_number=23).first()
        assert refreshed.status == 'Completed'

# ==============================================================================
# 2. CURRICULUM, CO-PO MATRIX & 48 SESSIONS TESTS
# ==============================================================================
def test_syllabus_7_modules_and_48_sessions(test_app):
    with test_app.app_context():
        modules = get_syllabus_modules('CSE3005')
        assert len(modules) == 7
        total_sessions = sum(m.total_sessions for m in modules)
        assert total_sessions == 48

        sessions = get_session_plans('CSE3005')
        assert len(sessions) == 48
        theory_count = sum(1 for s in sessions if s.session_type == 'Theory')
        lab_count = sum(1 for s in sessions if s.session_type == 'Lab')
        assert theory_count == 31
        assert lab_count == 17

def test_copo_mapping_matrix_exactness(test_app):
    with test_app.app_context():
        matrix = get_copo_matrix('CSE3005')
        assert 'CO1' in matrix
        assert 'CO2' in matrix
        assert 'CO3' in matrix
        # Check specific verified values from SE_CSE3005 PDF:
        assert matrix['CO1']['PO1'] == 2
        assert matrix['CO1']['PO2'] == 3
        assert matrix['CO1']['PO5'] == 3
        assert matrix['CO2']['PO1'] == 3
        assert matrix['CO2']['PO3'] == 3
        assert matrix['CO3']['PO9'] == 3

# ==============================================================================
# 3. STUDENT RECORDS, ATTENDANCE & WEAK STUDENTS TESTS
# ==============================================================================
def test_attendance_critical_shortage_filter(test_app):
    with test_app.app_context():
        records = get_attendance_records('CSE3005')
        assert len(records) == 58
        critical = [r for r in records if r.percentage < 75.0]
        # Verified 6 students below threshold
        assert len(critical) == 6
        for r in critical:
            assert r.status == 'Critical (<75%)'

def test_marks_and_weak_student_identification(test_app):
    with test_app.app_context():
        marks = get_marks_records('CSE3005')
        assert len(marks) == 174  # 58 students * 3 assessments
        weak_marks = [m for m in marks if m.is_weak_student]
        assert len(weak_marks) > 0
        for m in weak_marks:
            assert m.marks_obtained < 40.0

def test_attainment_calculation_service(test_app):
    with test_app.app_context():
        records = calculate_course_attainment('CSE3005')
        assert len(records) == 3
        for r in records:
            assert r.overall_attainment >= 70.0
            assert r.attainment_level == 3
            assert r.target_benchmark == 70.0

# ==============================================================================
# 4. SOFTWARE ENGINEERING MODULES (MoSCoW, UML, QA, SPM)
# ==============================================================================
def test_moscow_requirements_filter(test_app):
    with test_app.app_context():
        must_haves = get_requirements(moscow_filter='Must Have')
        should_haves = get_requirements(moscow_filter='Should Have')
        could_haves = get_requirements(moscow_filter='Could Have')
        wont_haves = get_requirements(moscow_filter="Won't Have")
        
        assert len(must_haves) >= 4
        assert len(should_haves) >= 2
        assert len(could_haves) >= 1
        assert len(wont_haves) >= 1

def test_architecture_diagrams_suite(test_app):
    with test_app.app_context():
        diagrams = get_architecture_diagrams()
        assert len(diagrams) >= 7
        types = [d.diagram_type for d in diagrams]
        assert 'Use Case' in types
        assert 'Class' in types
        assert 'Sequence' in types
        assert 'Context DFD' in types
        assert 'Level 1 DFD' in types
        assert 'Database ER' in types

def test_testing_management_qa_metrics(test_app):
    with test_app.app_context():
        qa_data = get_test_management_data()
        assert qa_data['metrics']['total'] >= 10
        assert qa_data['metrics']['passed'] >= 8
        assert float(qa_data['metrics']['passRate'].replace('%', '')) >= 80.0

def test_spm_pert_cpm_estimation_calculations(test_app):
    with test_app.app_context():
        spm = get_spm_dashboard_data()
        assert spm['cpmTotalDays'] > 10.0
        assert len(spm['perts']) >= 5
        for p in spm['perts']:
            # Formula check: TE = (a + 4m + b) / 6
            calc_te = round((p.optimistic_days + 4 * p.most_likely_days + p.pessimistic_days) / 6.0, 2)
            assert p.expected_days == calc_te
