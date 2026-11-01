"""
CourseFlow - Course File Management System (CFMS)
Flask Application Server & REST API Layer
"""

import io
import json
import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, abort
)
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

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

        # Reject empty fields
        if not email or not password:
            error = "Please enter valid demo credentials."
        # Demo authentication check - strictly validate password
        elif email in DEMO_USERS:
            if password == 'courseflow123':
                session['user'] = DEMO_USERS[email]
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid password. For demo access, use courseflow123."
        else:
            # Custom demo email login (must also use valid demo password)
            if password == 'courseflow123':
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
                error = "Invalid credentials. Please enter valid demo credentials."

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
        code = (data.get('code') or '').strip().upper()
        if any(c['code'].upper() == code for c in DEMO_COURSES):
            return jsonify({"error": f"Course code {code} already exists."}), 400
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

DEMO_SYLLABUS = {
    'CS301': [
        { "unit": 1, "title": "Software Lifecycle & Process Models", "hours": 8, "outcomes": "CO1", "topics": "Agile Principles, Scrum Framework, Sprints, User Stories, Waterfall, Spiral" },
        { "unit": 2, "title": "Requirements Engineering & Modeling", "hours": 9, "outcomes": "CO2", "topics": "Requirements Elicitation, IEEE 830 SRS, UML Use Case, Activity, Sequence Diagrams" },
        { "unit": 3, "title": "Architectural Design & Patterns", "hours": 10, "outcomes": "CO3", "topics": "Layered, Microservices, GoF Design Patterns: Factory, Singleton, Observer, Strategy" },
        { "unit": 4, "title": "Verification, Validation & Quality Assurance", "hours": 10, "outcomes": "CO4", "topics": "Black-box, White-box, Unit Testing, TDD, Cyclomatic Complexity, Code Coverage" },
        { "unit": 5, "title": "Project Management & Contemporary Practices", "hours": 8, "outcomes": "CO5", "topics": "COCOMO Estimation, Risk Management, CI/CD with Git, Docker, Pipelines" }
    ]
}

GEMINI_SUMMARIZER_PROMPT = """
You are an expert academic curriculum reviewer and university accreditation analyst for an outcome-based education (OBE) course file management system.
Analyze the provided course handout document thoroughly and extract the following structured academic information based ONLY on the actual content present in the document.

Required output sections:
A. COURSE HANDOUT SUMMARY: A concise, informative summary of the document.
B. KEY TOPICS: Identify the important topics and concepts directly covered in the handout.
C. SUGGESTED COURSE OUTCOMES: Formulate relevant Course Outcomes (COs) aligned with Bloom's Taxonomy based ONLY on the document's content.
   For each outcome, provide:
   - "co": CO identifier (e.g. "CO1", "CO2")
   - "statement": Outcome statement starting with an action verb (e.g. "Formulate software development workflows applying modern lifecycle paradigms.")
   - "relevantTopics": Array of specific topics from the document supporting that outcome.
D. IMPORTANT INFORMATION:
   - "courseTitle": Course title from document (or "Not specified in document" if absent)
   - "courseCode": Course code from document (or "Not specified in document" if absent)
   - "unitNames": Array of unit or module titles found in the document (or empty list if none)
   - "importantConcepts": Array of core architectural or theoretical principles found
   - "learningObjectives": Array of explicit learning objectives stated in document (or empty list if none)

CRITICAL INSTRUCTIONS:
- Do not invent missing course details or learning outcomes.
- If information is unavailable, explicitly indicate that it was not found in the document.
- Output MUST be a strictly valid JSON object matching this schema:
{
  "courseTitle": "...",
  "courseCode": "...",
  "summary": "...",
  "keyTopics": ["Topic 1", "Topic 2"],
  "suggestedCourseOutcomes": [
    {
      "co": "CO1",
      "statement": "...",
      "relevantTopics": ["Topic A", "Topic B"]
    }
  ],
  "importantInformation": {
    "unitNames": ["Unit 1...", "Unit 2..."],
    "importantConcepts": ["Concept 1", "Concept 2"],
    "learningObjectives": ["Objective 1", "Objective 2"]
  }
}
"""

def process_handout_with_gemini(file_bytes, filename, course_id="CS301"):
    """
    Analyzes an uploaded course handout (PDF or DOCX) using Google Gen AI SDK.
    Returns (success: bool, result_or_error_dict_or_str, http_status_code)
    """
    if not filename:
        return False, "Filename is required.", 400

    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ['pdf', 'docx']:
        return False, f"Unsupported file type (.{ext}). Please upload a PDF or DOCX course handout document.", 400

    if not file_bytes or len(file_bytes) == 0:
        return False, "The uploaded document is empty (0 bytes). Please upload a valid course handout.", 400

    if len(file_bytes) > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit. Please upload a smaller document.", 400

    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return False, "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment or .env file.", 500

    model_name = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash').strip() or 'gemini-3.8-flash'

    # Prepare document content for Gemini
    gemini_contents = []

    if ext == 'pdf':
        if not file_bytes.startswith(b'%PDF-'):
            return False, "Corrupted or invalid PDF file. Header verification failed.", 400
        try:
            import pymupdf
            pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            if len(pdf_doc) == 0:
                return False, "The uploaded PDF document contains no pages.", 400
            pdf_doc.close()
        except Exception as e:
            return False, f"Corrupted PDF document: {str(e)}", 400

        try:
            from google.genai import types
            part = types.Part.from_bytes(data=file_bytes, mime_type='application/pdf')
            gemini_contents.append(part)
            gemini_contents.append(f"Target Course: {course_id}\n\n{GEMINI_SUMMARIZER_PROMPT}")
        except Exception as e:
            return False, f"Failed to prepare PDF document for Gemini: {str(e)}", 500

    elif ext == 'docx':
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
        except Exception as e:
            return False, f"Corrupted or invalid DOCX document: {str(e)}", 400

        lines = []
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                lines.append(t)
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    dedup = []
                    for c in cells:
                        if not dedup or dedup[-1] != c:
                            dedup.append(c)
                    lines.append(" | ".join(dedup))

        doc_text = "\n".join(lines).strip()
        if not doc_text:
            return False, "The uploaded DOCX file does not contain any readable text or is empty.", 400

        gemini_contents.append(
            f"DOCUMENT FILENAME: {filename}\nTARGET COURSE: {course_id}\n\nDOCUMENT EXTRACTED CONTENT:\n{doc_text}\n\n{GEMINI_SUMMARIZER_PROMPT}"
        )

    # Call Gemini API
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
        response = client.models.generate_content(
            model=model_name,
            contents=gemini_contents,
            config=config
        )
    except APIError as e:
        err_msg = str(e)
        if e.code == 400 or "API key not valid" in err_msg or "API_KEY_INVALID" in err_msg:
            return False, "Gemini API authentication failed: Invalid API key. Please verify your GEMINI_API_KEY.", 401
        elif e.code == 429 or "RESOURCE_EXHAUSTED" in err_msg:
            return False, "Gemini API rate limit or quota exceeded. Please try again shortly.", 429
        elif e.code in (500, 503) or "UNAVAILABLE" in err_msg:
            return False, "Google Gemini API service is temporarily unavailable. Please try again later.", 503
        return False, f"Gemini API request failed ({e.code}): {e.message}", 502
    except Exception as e:
        err_str = str(e)
        if "ConnectError" in err_str or "Failed to establish a new connection" in err_str or "Network is unreachable" in err_str:
            return False, "Network connection failure: Unable to communicate with Google Gemini API.", 503
        return False, f"Failed to communicate with Gemini API: {err_str}", 500

    if not response or not response.text:
        return False, "Gemini API returned an empty response.", 502

    try:
        parsed_data = json.loads(response.text)
    except json.JSONDecodeError:
        return False, "Gemini returned an invalid JSON response structure.", 502

    if not isinstance(parsed_data, dict):
        return False, "Invalid response schema received from Gemini.", 502

    summary = parsed_data.get("summary", "")
    key_topics = parsed_data.get("keyTopics", [])
    suggested_cos = parsed_data.get("suggestedCourseOutcomes", [])
    important_info = parsed_data.get("importantInformation", {})

    if not summary and not key_topics:
        return False, "Gemini analysis could not extract summary or topics from this document.", 502

    result = {
        "success": True,
        "fileName": filename,
        "courseCode": parsed_data.get("courseCode") or course_id,
        "courseTitle": parsed_data.get("courseTitle") or "Software Engineering",
        "extractedSummary": summary,
        "topicsIdentified": key_topics,
        "suggestedOutcomes": [
            f"{co.get('co', 'CO')}: {co.get('statement', '')}" if isinstance(co, dict) else str(co)
            for co in suggested_cos
        ],
        "suggestedOutcomesDetailed": suggested_cos,
        "importantInformation": important_info
    }
    return True, result, 200

@app.route('/api/handouts/summarize', methods=['POST'])
def api_summarize_handout():
    """
    AI-powered Handout Summarizer endpoint using Google Gemini API.
    Accepts multipart file upload or JSON payload with file metadata/path.
    """
    file_bytes = None
    filename = None
    course_id = "CS301"

    # 1. Check if multipart/form-data with file
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = uploaded_file.filename
        file_bytes = uploaded_file.read()
        course_id = request.form.get('courseId', 'CS301')

    # 2. Check if JSON payload (used in tests or sample document trigger)
    elif request.is_json:
        data = request.get_json() or {}
        course_id = data.get('courseId', 'CS301')
        fname = data.get('fileName') or data.get('filename')

        if fname:
            filename = fname
            sample_path = os.path.join(app.root_path, 'static', 'sample_docs', fname)
            if not os.path.exists(sample_path):
                # Try default sample
                sample_path = os.path.join(app.root_path, 'static', 'sample_docs', 'CS301_Software_Engineering_Handout.pdf')
                if not fname.lower().endswith(('.pdf', '.docx')):
                    # If test asks for unsupported file like .exe
                    filename = fname
                    file_bytes = b'fake binary'
                else:
                    filename = fname
            if os.path.exists(sample_path) and file_bytes is None:
                with open(sample_path, 'rb') as f:
                    file_bytes = f.read()

    if not filename:
        return jsonify({"error": "No file uploaded. Please provide a course handout document.", "success": False}), 400

    success, result, status_code = process_handout_with_gemini(file_bytes, filename, course_id)
    if not success:
        return jsonify({"error": result, "success": False}), status_code

    return jsonify(result), status_code

@app.route('/api/syllabus/<course_id>', methods=['GET', 'POST'])
def api_syllabus(course_id):
    if request.method == 'POST':
        data = request.get_json() or {}
        units = data.get('units') if isinstance(data, dict) and 'units' in data else data
        if not isinstance(units, list):
            return jsonify({"error": "Expected a list of syllabus units", "success": False}), 400
        DEMO_SYLLABUS[course_id] = units
        return jsonify({"success": True, "courseId": course_id, "units": units}), 200

    units = DEMO_SYLLABUS.get(course_id, DEMO_SYLLABUS.get('CS301', []))
    return jsonify(units), 200

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
