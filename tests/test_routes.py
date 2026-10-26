"""
CourseFlow (CFMS) - Automated Test Suite
Tests for Page Routes, Authentication, Role-Based Access, and REST APIs.
"""

import pytest
from app import app, DEMO_USERS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

def test_login_page_renders(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Sign In to CourseFlow" in response.data
    assert b"faculty@courseflow.demo" in response.data
    assert b"admin@courseflow.demo" in response.data

def test_login_faculty_success(client):
    response = client.post('/login', data={
        'email': 'faculty@courseflow.demo',
        'password': 'courseflow123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Good morning" in response.data

def test_login_admin_success(client):
    response = client.post('/login', data={
        'email': 'admin@courseflow.demo',
        'password': 'courseflow123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Good morning" in response.data
    # Admin section should appear in sidebar
    assert b"Faculty Management" in response.data

def test_logout(client):
    client.post('/login', data={'email': 'faculty@courseflow.demo', 'password': 'courseflow123'})
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In to CourseFlow" in response.data

def test_faculty_pages_accessible(client):
    with client.session_transaction() as sess:
        sess['user'] = DEMO_USERS['faculty@courseflow.demo']

    routes = [
        '/dashboard',
        '/courses',
        '/courses/CS301',
        '/syllabus',
        '/session-planner',
        '/students',
        '/assessments',
        '/marks',
        '/attendance',
        '/feedback',
        '/outcomes',
        '/attainment',
        '/ai-assistant',
        '/course-file',
        '/course-file/preview'
    ]

    for route in routes:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} failed with status {res.status_code}"

def test_role_based_access_faculty_forbidden(client):
    with client.session_transaction() as sess:
        sess['user'] = DEMO_USERS['faculty@courseflow.demo']

    admin_routes = [
        '/admin/faculty',
        '/admin/courses',
        '/admin/assignments',
        '/admin/monitoring'
    ]

    for route in admin_routes:
        res = client.get(route)
        assert res.status_code == 403, f"Faculty should be blocked from {route}"
        assert b"403 - Restricted Access" in res.data

def test_role_based_access_admin_allowed(client):
    with client.session_transaction() as sess:
        sess['user'] = DEMO_USERS['admin@courseflow.demo']

    admin_routes = [
        '/admin/faculty',
        '/admin/courses',
        '/admin/assignments',
        '/admin/monitoring'
    ]

    for route in admin_routes:
        res = client.get(route)
        assert res.status_code == 200, f"Admin should have access to {route}"

def test_api_endpoints(client):
    # GET /api/courses
    res = client.get('/api/courses')
    assert res.status_code == 200
    courses = res.get_json()
    assert len(courses) >= 4
    assert any(c['code'] == 'CS301' for c in courses)

    # GET /api/courses/CS301
    res_single = client.get('/api/courses/CS301')
    assert res_single.status_code == 200
    assert res_single.get_json()['code'] == 'CS301'

    # POST /api/handouts/summarize
    res_ai = client.post('/api/handouts/summarize', json={'fileName': 'syllabus.pdf'})
    assert res_ai.status_code == 200
    data_ai = res_ai.get_json()
    assert data_ai['success'] is True
    assert 'topicsIdentified' in data_ai
    assert len(data_ai['suggestedOutcomes']) > 0

    # POST /api/course-files/generate
    res_gen = client.post('/api/course-files/generate', json={'courseId': 'CS301'})
    assert res_gen.status_code == 200
    assert res_gen.get_json()['success'] is True

def test_switch_role_api(client):
    res = client.post('/api/switch-role', json={'role': 'admin'})
    assert res.status_code == 200
    assert res.get_json()['user']['role'] == 'admin'

    res2 = client.post('/api/switch-role', json={'role': 'faculty'})
    assert res2.status_code == 200
    assert res2.get_json()['user']['role'] == 'faculty'

def test_404_error_handler(client):
    res = client.get('/nonexistent-academic-route')
    assert res.status_code == 404
    assert b"404 - Page Not Found" in res.data
