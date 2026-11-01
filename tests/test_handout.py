"""
CourseFlow (CFMS) - Module 7 Test Suite
Course Handout Summarizer (Google Gemini AI Integration)
Tests for M7-TC01, M7-TC02, M7-TC03, M7-TC04, and Error Handling.
"""

import io
import os
import pytest
from app import app, process_handout_with_gemini, DEMO_SYLLABUS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

# ==============================================================================
# M7-TC01: Load a sample course handout
# Expected: File preview / sample document is available and valid
# ==============================================================================
def test_m7_tc01_load_sample_handout_available(client):
    """
    M7-TC01: Verify that sample course handouts (PDF and DOCX) exist on the server
    and can be retrieved by the frontend for file preview.
    """
    # 1. Test sample PDF
    res_pdf = client.get('/static/sample_docs/CS301_Software_Engineering_Handout.pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.data.startswith(b'%PDF-')
    assert len(res_pdf.data) > 500

    # 2. Test sample DOCX
    res_docx = client.get('/static/sample_docs/CS301_Software_Engineering_Handout.docx')
    assert res_docx.status_code == 200
    assert len(res_docx.data) > 1000

# ==============================================================================
# M7-TC02: Upload an unsupported file such as .exe
# Expected: Rejected with a validation message
# ==============================================================================
def test_m7_tc02_reject_unsupported_file_extension(client):
    """
    M7-TC02: Uploading an unsupported executable (.exe) must be rejected
    with a clear 400 validation error message.
    """
    data = {
        'file': (io.BytesIO(b'MZ\x90\x00\x03\x00\x00\x00binary_executable_code'), 'malicious_setup.exe'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json['success'] is False
    assert "Unsupported file type" in res_json['error']
    assert ".exe" in res_json['error']

def test_m7_tc02_reject_unsupported_bat_file(client):
    """
    M7-TC02: Uploading a script (.bat) must also be rejected.
    """
    data = {
        'file': (io.BytesIO(b'@echo off\necho hello'), 'script.bat'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json['success'] is False
    assert "Unsupported file type" in res_json['error']

# ==============================================================================
# M7-TC03: Generate a summary with Gemini AI
# Expected: Real Gemini API request is made and structured summary,
# topics, and suggested Course Outcomes are generated.
# ==============================================================================
def test_m7_tc03_generate_summary_real_gemini_pdf(client):
    """
    M7-TC03: Upload a real course handout PDF and verify that Google Gemini API
    processes the document and returns structured summary, topics, and COs.
    """
    sample_path = os.path.join(app.root_path, 'static', 'sample_docs', 'CS301_Software_Engineering_Handout.pdf')
    with open(sample_path, 'rb') as f:
        pdf_bytes = f.read()

    data = {
        'file': (io.BytesIO(pdf_bytes), 'CS301_Software_Engineering_Handout.pdf'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_json = response.get_json()

    assert res_json['success'] is True
    assert res_json['fileName'] == 'CS301_Software_Engineering_Handout.pdf'

    # Section A: Summary
    assert 'extractedSummary' in res_json
    assert len(res_json['extractedSummary']) > 20

    # Section B: Topics
    assert 'topicsIdentified' in res_json
    assert isinstance(res_json['topicsIdentified'], list)
    assert len(res_json['topicsIdentified']) >= 2

    # Section C: Suggested Course Outcomes
    assert 'suggestedOutcomes' in res_json
    assert len(res_json['suggestedOutcomes']) >= 2
    assert any('CO' in str(co) for co in res_json['suggestedOutcomes'])

    # Section D: Important Information
    assert 'importantInformation' in res_json
    assert isinstance(res_json['importantInformation'], dict)

def test_m7_tc03_generate_summary_real_gemini_docx(client):
    """
    M7-TC03: Upload a real course handout DOCX and verify that python-docx extracts
    the text and Google Gemini API processes and returns structured summary and COs.
    """
    sample_path = os.path.join(app.root_path, 'static', 'sample_docs', 'CS301_Software_Engineering_Handout.docx')
    with open(sample_path, 'rb') as f:
        docx_bytes = f.read()

    data = {
        'file': (io.BytesIO(docx_bytes), 'CS301_Software_Engineering_Handout.docx'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_json = response.get_json()

    assert res_json['success'] is True
    assert len(res_json['topicsIdentified']) >= 2
    assert len(res_json['suggestedOutcomes']) >= 2

# ==============================================================================
# M7-TC04: Faculty Approve and Save into Syllabus
# Expected: Approved units and outcomes are saved into the course syllabus.
# ==============================================================================
def test_m7_tc04_approve_and_save_into_syllabus(client):
    """
    M7-TC04: When faculty approves the generated summary, the structured units
    are saved into the selected course's syllabus and retrieved successfully.
    """
    course_id = 'CS301'
    new_approved_units = [
        {
            "unit": 1,
            "title": "Software Process Models & Agile Principles",
            "hours": 8,
            "outcomes": "CO1",
            "topics": "Waterfall, Prototyping, Spiral, Agile Scrum framework"
        },
        {
            "unit": 2,
            "title": "Requirements Engineering & IEEE SRS",
            "hours": 9,
            "outcomes": "CO2",
            "topics": "Requirements elicitation, IEEE 830, UML diagrams"
        },
        {
            "unit": 3,
            "title": "Architectural Design & Gang-of-Four Patterns",
            "hours": 10,
            "outcomes": "CO3",
            "topics": "Microservices, Factory, Singleton, Observer, Strategy"
        }
    ]

    # Save approved syllabus units
    save_res = client.post(f'/api/syllabus/{course_id}', json={'units': new_approved_units})
    assert save_res.status_code == 200
    save_data = save_res.get_json()
    assert save_data['success'] is True
    assert len(save_data['units']) == 3

    # Retrieve syllabus and verify persistence
    get_res = client.get(f'/api/syllabus/{course_id}')
    assert get_res.status_code == 200
    retrieved_units = get_res.get_json()
    assert len(retrieved_units) == 3
    assert retrieved_units[0]['title'] == "Software Process Models & Agile Principles"
    assert retrieved_units[1]['outcomes'] == "CO2"

# ==============================================================================
# ADDITIONAL ERROR HANDLING TESTS
# ==============================================================================
def test_reject_empty_document(client):
    """
    Upload of an empty file (0 bytes) must return a clear 400 error.
    """
    data = {
        'file': (io.BytesIO(b''), 'empty_handout.pdf'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json['success'] is False
    assert "empty" in res_json['error'].lower()

def test_reject_corrupted_pdf(client):
    """
    Upload of a corrupted PDF file (invalid header) must return a clear 400 error.
    """
    data = {
        'file': (io.BytesIO(b'NOT_A_VALID_PDF_HEADER_12345'), 'corrupted_handout.pdf'),
        'courseId': 'CS301'
    }
    response = client.post('/api/handouts/summarize', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json['success'] is False
    assert "corrupted" in res_json['error'].lower() or "header" in res_json['error'].lower()

def test_handle_missing_api_key(monkeypatch):
    """
    When GEMINI_API_KEY is not set, must return a helpful 500 error.
    """
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    success, error_msg, status_code = process_handout_with_gemini(b'%PDF-1.4 test', 'handout.pdf')
    assert success is False
    assert status_code == 500
    assert "Gemini API key is not configured" in error_msg

def test_handle_invalid_api_key(monkeypatch):
    """
    When GEMINI_API_KEY is invalid, must return a 401 authentication error.
    """
    monkeypatch.setenv('GEMINI_API_KEY', 'invalid_api_key_test_xyz')
    sample_path = os.path.join(app.root_path, 'static', 'sample_docs', 'CS301_Software_Engineering_Handout.pdf')
    with open(sample_path, 'rb') as f:
        pdf_bytes = f.read()

    success, error_msg, status_code = process_handout_with_gemini(pdf_bytes, 'handout.pdf')
    assert success is False
    assert status_code == 401
    assert "Invalid API key" in error_msg
