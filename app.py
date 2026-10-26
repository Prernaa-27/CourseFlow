"""
CourseFlow - Course File Management System (CFMS)
Flask Application Server & REST API Layer
"""

import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, abort
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'courseflow-cfms-dev-secret-key-2024')

# ==============================================================================
# DEMO DATA STORE
# ==============================================================================
DEMO_COURSES = [
    {
        "id": "CS301",
        "code": "CS301",
        "title": "Software Engineering",
        "semester": "Semester 5",
        "academicYear": "2024-2025",
        "faculty": "Dr. Sarah Jenkins",
        "facultyEmail": "faculty@courseflow.demo",
        "studentsCount": 58,
        "completion": 85,
        "status": "In Progress",
        "credits": 4,
        "department": "Computer Science & Engineering",
        "description": "Comprehensive study of software lifecycle models, requirements engineering, architectural design, agile methodologies, testing techniques, and project management."
    },
    {
        "id": "CS302",
        "code": "CS302",
        "title": "Database Management Systems",
        "semester": "Semester 5",
        "academicYear": "2024-2025",
        "faculty": "Dr. Sarah Jenkins",
        "facultyEmail": "faculty@courseflow.demo",
        "studentsCount": 62,
        "completion": 100,
        "status": "Completed",
        "credits": 4,
        "department": "Computer Science & Engineering",
        "description": "Relational data models, normalization, SQL, indexing, transaction processing, concurrency control, and NoSQL architecture."
    },
    {
        "id": "CS303",
        "code": "CS303",
        "title": "Design & Analysis of Algorithms",
        "semester": "Semester 5",
        "academicYear": "2024-2025",
        "faculty": "Prof. Rajesh Sharma",
        "facultyEmail": "admin@courseflow.demo",
        "studentsCount": 55,
        "completion": 72,
        "status": "In Progress",
        "credits": 4,
        "department": "Computer Science & Engineering",
        "description": "Asymptotic notation, divide-and-conquer, greedy techniques, dynamic programming, graph algorithms, and NP-completeness."
    },
    {
        "id": "CS401",
        "code": "CS401",
        "title": "Cloud Computing & DevOps",
        "semester": "Semester 7",
        "academicYear": "2024-2025",
        "faculty": "Dr. Sarah Jenkins",
        "facultyEmail": "faculty@courseflow.demo",
        "studentsCount": 48,
        "completion": 94,
        "status": "Under Review",
        "credits": 3,
        "department": "Computer Science & Engineering",
        "description": "Virtualization, microservices, containerization with Docker & Kubernetes, CI/CD pipelines, and cloud security."
    },
    {
        "id": "CS202",
        "code": "CS202",
        "title": "Object-Oriented Programming (Java)",
        "semester": "Semester 3",
        "academicYear": "2024-2025",
        "faculty": "Dr. Sarah Jenkins",
        "facultyEmail": "faculty@courseflow.demo",
        "studentsCount": 65,
        "completion": 38,
        "status": "Draft",
        "credits": 4,
        "department": "Computer Science & Engineering",
        "description": "Encapsulation, inheritance, polymorphism, Java collections framework, exception handling, and concurrent programming."
    }
]

DEMO_USERS = {
    "faculty@courseflow.demo": {
        "name": "Dr. Sarah Jenkins",
        "email": "faculty@courseflow.demo",
        "role": "faculty",
        "department": "Computer Science & Engineering",
        "avatar": "SJ"
    },
    "admin@courseflow.demo": {
        "name": "Prof. Rajesh Sharma",
        "email": "admin@courseflow.demo",
        "role": "admin",
        "department": "Academic Affairs / Dean CSE",
        "avatar": "RS"
    }
}

# ==============================================================================
# AUTHENTICATION HELPERS & DECORATORS
# ==============================================================================
def get_current_user():
    return session.get('user')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Default to faculty for immediate seamless local inspection
            session['user'] = DEMO_USERS['faculty@courseflow.demo']
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            return render_template('403.html', user=user, active_page='403'), 403
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_vars():
    user = session.get('user', DEMO_USERS['faculty@courseflow.demo'])
    return dict(user=user)

# ==============================================================================
# AUTHENTICATION ROUTES
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        # Demo authentication check
        if email in DEMO_USERS and (password == 'courseflow123' or password != ''):
            session['user'] = DEMO_USERS[email]
            return redirect(url_for('dashboard'))
        elif email != '':
            # Allow custom demo faculty login
            role = 'admin' if 'admin' in email else 'faculty'
            user_data = {
                "name": "Prof. " + email.split('@')[0].replace('.', ' ').title(),
                "email": email,
                "role": role,
                "department": "Computer Science & Engineering",
                "avatar": email[:2].upper()
            }
            session['user'] = user_data
            return redirect(url_for('dashboard'))
        else:
            error = "Please enter valid demo credentials."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/switch-role', methods=['POST'])
def switch_role():
    data = request.get_json() or {}
    new_role = data.get('role', 'faculty')
    if new_role == 'admin':
        session['user'] = DEMO_USERS['admin@courseflow.demo']
    else:
        session['user'] = DEMO_USERS['faculty@courseflow.demo']
    return jsonify({"success": True, "user": session['user']})

# ==============================================================================
# MAIN APPLICATION PAGES
# ==============================================================================
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/courses')
@login_required
def courses():
    return render_template('courses.html', active_page='courses', courses=DEMO_COURSES)

@app.route('/courses/<course_id>')
@login_required
def course_detail(course_id):
    course = next((c for c in DEMO_COURSES if c['id'] == course_id), None)
    if not course:
        # Fallback to first course
        course = DEMO_COURSES[0]
    
    # Form status badge HTML
    status_badge = f'<span class="badge-status badge-status-inprogress"><i class="bi bi-hourglass-split"></i> {course["status"]}</span>'
    if course['status'] == 'Completed':
        status_badge = f'<span class="badge-status badge-status-completed"><i class="bi bi-check-circle-fill"></i> {course["status"]}</span>'
    elif course['status'] == 'Draft':
        status_badge = f'<span class="badge-status badge-status-draft"><i class="bi bi-circle"></i> {course["status"]}</span>'

    return render_template('course_detail.html', active_page='course_detail', course=course, status_badge=status_badge)

@app.route('/syllabus')
@login_required
def syllabus():
    return render_template('syllabus.html', active_page='syllabus')

@app.route('/session-planner')
@app.route('/session_planner')
@login_required
def session_planner():
    return render_template('session_planner.html', active_page='session_planner')

@app.route('/students')
@login_required
def students():
    return render_template('students.html', active_page='students')

@app.route('/assessments')
@login_required
def assessments():
    return render_template('assessments.html', active_page='assessments')

@app.route('/marks')
@login_required
def marks():
    return render_template('marks.html', active_page='marks')

@app.route('/attendance')
@login_required
def attendance():
    return render_template('attendance.html', active_page='attendance')

@app.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html', active_page='feedback')

@app.route('/outcomes')
@login_required
def outcomes():
    return render_template('outcomes.html', active_page='outcomes')

@app.route('/attainment')
@login_required
def attainment():
    return render_template('attainment.html', active_page='attainment')

@app.route('/ai-assistant')
@app.route('/ai_assistant')
@login_required
def ai_assistant():
    return render_template('ai_assistant.html', active_page='ai_assistant')

@app.route('/course-file')
@app.route('/course_file')
@login_required
def course_file():
    return render_template('course_file.html', active_page='course_file')

@app.route('/course-file/preview')
@app.route('/course_file_preview')
@login_required
def course_file_preview():
    return render_template('course_file_preview.html', active_page='course_file_preview')

# ==============================================================================
# ADMINISTRATOR MODULE PAGES
# ==============================================================================
@app.route('/admin/faculty')
@login_required
@admin_required
def admin_faculty():
    return render_template('admin_faculty.html', active_page='admin_faculty')

@app.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    return render_template('admin_courses.html', active_page='admin_courses')

@app.route('/admin/assignments')
@login_required
@admin_required
def admin_assignments():
    return render_template('admin_assignments.html', active_page='admin_assignments')

@app.route('/admin/monitoring')
@login_required
@admin_required
def admin_monitoring():
    return render_template('admin_monitoring.html', active_page='admin_monitoring')

# ==============================================================================
# REST API CONTRACTS & INTEGRATION ENDPOINTS
# ==============================================================================
@app.route('/api/current-user')
def api_current_user():
    return jsonify(get_current_user() or DEMO_USERS['faculty@courseflow.demo'])

@app.route('/api/courses', methods=['GET', 'POST'])
def api_courses():
    if request.method == 'POST':
        data = request.get_json() or {}
        DEMO_COURSES.append(data)
        return jsonify(data), 201
    return jsonify(DEMO_COURSES)

@app.route('/api/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def api_course_detail(course_id):
    course = next((c for c in DEMO_COURSES if c['id'] == course_id), None)
    if not course and request.method != 'DELETE':
        return jsonify({"error": "Course not found"}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        course.update(data)
        return jsonify(course)
    elif request.method == 'DELETE':
        return jsonify({"success": True})
    return jsonify(course)

@app.route('/api/handouts/summarize', methods=['POST'])
def api_summarize_handout():
    """
    Contract endpoint for future AI/LLM integration.
    Accepts file metadata or multipart file.
    """
    return jsonify({
        "success": True,
        "courseCode": "CS301",
        "courseTitle": "Software Engineering",
        "topicsIdentified": [
            "Software Process Models (Agile, Waterfall, Spiral)",
            "Requirements Analysis, Use Cases, IEEE-830 SRS",
            "Architectural Design, Microservices, GoF Patterns",
            "Verification, Unit Testing, Cyclomatic Complexity",
            "Project Estimation, COCOMO, CI/CD Pipeline Automation"
        ],
        "suggestedOutcomes": [
            "CO1: Formulate software development workflows applying modern lifecycle paradigms.",
            "CO2: Construct formal requirements specifications using UML modeling diagrams.",
            "CO3: Synthesize modular architectural designs using industry design patterns.",
            "CO4: Implement automated testing and continuous integration suites."
        ],
        "recommendedHours": 45,
        "extractedSummary": "This course provides foundational and applied competencies in engineering large-scale, dependable software systems. It emphasizes agile collaboration, architectural discipline, testing rigor, and lifecycle automation according to contemporary industry standards."
    })

@app.route('/api/course-files/generate', methods=['POST'])
def api_generate_course_file():
    """
    Contract endpoint for future backend PDF generation service.
    """
    data = request.get_json() or {}
    course_id = data.get('courseId', 'CS301')
    return jsonify({
        "success": True,
        "courseId": course_id,
        "dossierUrl": f"/course-file/preview?course_id={course_id}",
        "status": "Generated"
    })

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================
@app.errorhandler(403)
def forbidden(e):
    user = session.get('user', DEMO_USERS['faculty@courseflow.demo'])
    return render_template('403.html', user=user, active_page='403'), 403

@app.errorhandler(404)
def not_found(e):
    user = session.get('user', DEMO_USERS['faculty@courseflow.demo'])
    return render_template('404.html', user=user, active_page='404'), 404

@app.errorhandler(500)
def server_error(e):
    user = session.get('user', DEMO_USERS['faculty@courseflow.demo'])
    return render_template('404.html', user=user, active_page='500'), 500

if __name__ == '__main__':
    # Run locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
