"""
HCI (CSE2724) Primary Course, OBE Attainment & Excel Import Tests
"""

import io
import pytest
from app import app
from database import db
from models.course import Course
from services.course_service import get_course_by_id, get_course_summary_metrics
from services.attainment_service import calculate_course_attainment, calculate_program_outcome_attainment
from services.student_service import get_students_for_course, get_assessments_for_course

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user'] = {
                'email': 'faculty@courseflow.demo',
                'role': 'faculty',
                'name': 'Dr. Shilpa Mahajan'
            }
        yield client

def test_cse2724_is_primary_course():
    """Verify that CSE2724 is registered as course in database."""
    with app.app_context():
        course = get_course_by_id('CSE2724')
        assert course is not None
        assert course.code == 'CSE2724'
        assert 'Human Computer Interaction' in course.title
        assert course.status == 'Completed'

def test_cse2724_student_count_and_enrolment():
    """Verify that all 391 students from CSE2724.xlsx are enrolled."""
    with app.app_context():
        students = get_students_for_course('CSE2724')
        assert len(students) == 391

def test_cse2724_assessments_and_weightages():
    """Verify assessment components for CSE2724 (Lab 30, Project 30, End Term 40)."""
    with app.app_context():
        assessments = get_assessments_for_course('CSE2724')
        assert len(assessments) == 3
        weights = {a.name: a.weightage_percent for a in assessments}
        assert weights.get('Lab Assessment') == 30.0
        assert weights.get('Project') == 30.0
        assert weights.get('End term examination') == 40.0

def test_cse2724_obe_attainment_and_no_minilines():
    """Verify OBE attainment engine and that unmapped POs are omitted (preventing mini-lines)."""
    with app.app_context():
        co_res = calculate_course_attainment('CSE2724')
        assert len(co_res) == 3
        for rec in co_res:
            assert rec.attainment_level == 3
            assert rec.attainment_percentage >= rec.target_benchmark
        
        po_res = calculate_program_outcome_attainment('CSE2724')
        mapped_pos = po_res.get('mappedOnly', [])
        # PO6, PO8, PO9, PO12 are unmapped in CSE2724.xlsx and must NOT be in mappedOnly
        mapped_codes = [p['code'] for p in mapped_pos]
        assert 'PO1' in mapped_codes
        assert 'PO2' in mapped_codes
        assert 'PO6' not in mapped_codes
        assert 'PO8' not in mapped_codes
        assert 'PO9' not in mapped_codes
        assert 'PO12' not in mapped_codes

def test_dashboard_defaults_to_cse2724(client):
    """Verify that opening the dashboard renders CSE2724 and its metrics."""
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'CSE2724' in html
    assert 'CSE2724 - HCI (Primary)' in html

def test_25_section_preview_renders_completely(client):
    """Verify that the official 25-section course file preview renders all sections."""
    res = client.get('/course-file/preview?course=CSE2724')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'BML Munjal University' in html
    assert 'Dr. Shilpa Mahajan' in html
    assert '1. Course Details' in html
    assert '2. Vision and Mission of the University' in html
    assert '11. Registered Students List' in html
    assert '13. Mid-Semester Question Papers' in html
    assert '14. Evaluated Submissions' in html
    assert '18. Complete Marks Register' in html
    assert '20. Final Result Analysis' in html
    assert '24. Faculty Course Review Report (Dr. Shilpa Mahajan)' in html
    assert '25. Additional Information & Complete Course Portfolio' in html

def test_cse2724_pass_rate_is_99_49_percent(client):
    """Verify that calculated pass rate strictly matches authentic 99.49% (389 passed, 2 failed)."""
    res = client.get('/course-file/preview?course=CSE2724')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert '99.49%' in html
    assert '389' in html
    assert '230C2030245' in html  # Rajyawardhan Godara (7.0/100)
    assert '230C2030266' in html  # Naman Wadhwa (33.0/100)

def test_attendance_apis_and_shortages(client):
    """Verify session recording, individual student overrides, and shortage filtering."""
    # 1. Shortages filter
    res = client.get('/api/attendance/CSE2724/shortages?threshold=75.0')
    assert res.status_code == 200
    data = res.get_json()
    assert data['threshold'] == 75.0
    assert data['shortageCount'] == 10
    assert len(data['students']) == 10

    # 2. Individual override
    res_override = client.post('/api/attendance/CSE2724/student/230C2030010', json={
        'attendedClasses': 15,
        'totalClasses': 16,
        'reason': 'Compensatory practical completed'
    })
    assert res_override.status_code == 200
    over_data = res_override.get_json()
    assert over_data['success'] is True
    assert over_data['record']['attendedClasses'] == 15

def test_course_file_section_upload_and_documents(client):
    """Verify evidence document upload and notes updating for course file sections."""
    # Test uploading evidence with mock file
    file_bytes = io.BytesIO(b'%PDF-1.4 Mock Question Paper Content for Section 13')
    res = client.post('/api/course-files/CSE2724/sections/13/upload', data={
        'file': (file_bytes, 'mid_sem_paper_hci_2024.pdf'),
        'notes': 'Mid-semester question papers with model answers attached for audit.',
        'status': 'Completed'
    }, content_type='multipart/form-data')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['section']['sectionNumber'] == 13
    assert data['section']['status'] == 'Completed'
    assert 'mid_sem_paper_hci_2024.pdf' in data['document']['fileName']

    # Test retrieving attached documents
    res_docs = client.get('/api/course-files/CSE2724/sections/13/documents')
    assert res_docs.status_code == 200
    docs = res_docs.get_json()
    assert len(docs) >= 1
    assert any(d['fileName'] == 'mid_sem_paper_hci_2024.pdf' for d in docs)
