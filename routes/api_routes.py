"""
CourseFlow REST API Layer
Connects frontend JavaScript directly to the PostgreSQL / SQLAlchemy Database.
"""

import io
import os
import json
from flask import Blueprint, request, jsonify, session, current_app
from database import db
from models import (
    Course, User, CourseFileSection, CourseDocument, SyllabusModule, SessionPlan,
    Student, StudentEnrolment, AttendanceRecord, StudentMark, Assessment, CourseOutcome, CO_PO_Mapping,
    StudentFeedback, Intervention, COAttainmentRecord, ProjectRequirement,
    ArchitectureDiagram, TestCase, ProjectMilestone, ProjectTask, RiskItem, PertEstimation, AuditLog
)
from services.course_service import get_all_courses, get_course_by_id, update_section_status
from services.curriculum_service import get_syllabus_modules, get_session_plans, get_course_outcomes, get_copo_matrix
from services.student_service import get_students_for_course, get_attendance_records, get_marks_records, get_assessments_for_course
from services.attainment_service import calculate_course_attainment, calculate_program_outcome_attainment
from services.excel_import_service import inspect_excel_workbook, preview_sheet_data, execute_excel_import
from services.se_service import get_requirements, get_architecture_diagrams, get_test_management_data, get_spm_dashboard_data

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==============================================================================
# COURSES & FACULTY APIS
# ==============================================================================
@api_bp.route('/courses', methods=['GET', 'POST'])
def handle_courses():
    if request.method == 'POST':
        data = request.get_json() or {}
        code = (data.get('code') or '').strip().upper()
        if Course.query.filter_by(code=code).first():
            return jsonify({"error": f"Course code {code} already exists."}), 400

        course = Course(
            id=code or 'CSE3005',
            code=code or 'CSE3005',
            title=data.get('title', 'Software Engineering'),
            semester=data.get('semester', 'Semester 4'),
            academic_year=data.get('academicYear', '2026-27'),
            credits=int(data.get('credits', 3)),
            department=data.get('department', 'Computer Science & Engineering'),
            description=data.get('description', ''),
            status='In Progress'
        )
        db.session.add(course)
        db.session.commit()
        return jsonify(course.to_dict()), 201

    courses = get_all_courses()
    return jsonify([c.to_dict() for c in courses])

@api_bp.route('/courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_course_detail(course_id):
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        course.title = data.get('title', course.title)
        course.semester = data.get('semester', course.semester)
        course.status = data.get('status', course.status)
        if 'credits' in data:
            course.credits = int(data['credits'])
        if 'description' in data:
            course.description = data['description']
        db.session.commit()
        return jsonify(course.to_dict())

    if request.method == 'DELETE':
        db.session.delete(course)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Course deleted'})

    return jsonify(course.to_dict())

@api_bp.route('/faculty', methods=['GET'])
def get_faculty_list():
    users = User.query.filter_by(role='faculty').all()
    return jsonify([u.to_dict() for u in users])

# ==============================================================================
# COURSE FILE SECTIONS (25 SECTIONS)
# ==============================================================================
@api_bp.route('/course-files/<course_id>/sections', methods=['GET'])
def get_course_sections(course_id):
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify([s.to_dict() for s in course.sections])

@api_bp.route('/course-files/<course_id>/sections/<int:section_number>', methods=['PUT'])
def update_section(course_id, section_number):
    data = request.get_json() or {}
    status = data.get('status', 'In Progress')
    notes = data.get('notes')
    user_id = session.get('user', {}).get('id')
    sec = update_section_status(course_id, section_number, status, notes, user_id)
    if not sec:
        return jsonify({'error': 'Section not found'}), 404
    return jsonify(sec.to_dict())

@api_bp.route('/course-files/<course_id>/sections/<int:section_number>/upload', methods=['POST'])
def upload_section_document(course_id, section_number):
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'error': 'Course not found'}), 404
    sec = CourseFileSection.query.filter_by(course_id=course.id, section_number=section_number).first()
    if not sec:
        return jsonify({'success': False, 'error': 'Section not found'}), 404

    user_id = session.get('user', {}).get('id')
    notes = request.form.get('notes')
    status = request.form.get('status')
    if not notes and request.is_json:
        data = request.get_json() or {}
        notes = data.get('notes')
        status = data.get('status')

    saved_doc = None
    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        save_dir = os.path.join(current_app.root_path, 'uploads', 'course_files', course.id, f'sec_{section_number}')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(filename)[1].lower()

        doc = CourseDocument(
            course_id=course.id,
            section_id=sec.id,
            file_name=filename,
            file_path=os.path.relpath(file_path, current_app.root_path).replace('\\', '/'),
            file_type=file_ext,
            file_size_bytes=file_size,
            uploaded_by_id=user_id
        )
        db.session.add(doc)
        sec.status = 'Completed' if status is None else status
        saved_doc = {
            'fileName': filename,
            'filePath': doc.file_path,
            'fileSize': file_size
        }

    if notes:
        sec.notes = notes
    if status:
        sec.status = status
    if user_id:
        sec.updated_by_id = user_id
    sec.updated_at = db.func.current_timestamp()

    log = AuditLog(
        user_id=user_id,
        action='UPLOAD_SECTION_EVIDENCE',
        module='Course File',
        details=f"Updated evidence/notes for Section {section_number} ({sec.title}) in {course.id}."
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Section {section_number} evidence updated successfully.',
        'section': sec.to_dict(),
        'document': saved_doc
    })

@api_bp.route('/course-files/<course_id>/sections/<int:section_number>/documents', methods=['GET'])
def get_section_documents(course_id, section_number):
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    sec = CourseFileSection.query.filter_by(course_id=course.id, section_number=section_number).first()
    if not sec:
        return jsonify({'error': 'Section not found'}), 404
    return jsonify([d.to_dict() for d in sec.documents])

# ==============================================================================
# SYLLABUS & CURRICULUM APIS
# ==============================================================================
@api_bp.route('/syllabus/<course_id>', methods=['GET', 'POST', 'PUT'])
def get_or_update_syllabus(course_id):
    if request.method in ['POST', 'PUT']:
        data = request.get_json() or {}
        units = data.get('units') or data.get('modules') or []
        for u in units:
            m_num = u.get('unit') or u.get('module_number') or 1
            mod = SyllabusModule.query.filter_by(course_id=course_id, module_number=m_num).first()
            if not mod:
                mod = SyllabusModule(
                    course_id=course_id,
                    module_number=m_num,
                    title=u.get('title', f'Module {m_num}'),
                    detailed_topics=u.get('topics', ''),
                    mapped_cos=u.get('outcomes', 'CO1'),
                    total_sessions=u.get('hours', 6)
                )
                db.session.add(mod)
            else:
                mod.title = u.get('title', mod.title)
                mod.detailed_topics = u.get('topics', mod.detailed_topics)
                mod.mapped_cos = u.get('outcomes', mod.mapped_cos)
                mod.total_sessions = u.get('hours', mod.total_sessions)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Syllabus updated successfully', 'units': units})

    modules = get_syllabus_modules(course_id)
    return jsonify([{
        'unit': m.module_number,
        'title': m.title,
        'hours': m.total_sessions,
        'outcomes': m.mapped_cos,
        'topics': m.detailed_topics
    } for m in modules])

@api_bp.route('/syllabus/<course_id>/sessions', methods=['GET'])
@api_bp.route('/curriculum/<course_id>/sessions', methods=['GET'])
def get_sessions(course_id):
    sessions = get_session_plans(course_id)
    return jsonify([s.to_dict() for s in sessions])

@api_bp.route('/outcomes/<course_id>', methods=['GET'])
def get_outcomes(course_id):
    cos = get_course_outcomes(course_id)
    matrix = get_copo_matrix(course_id)
    return jsonify({
        'outcomes': [co.to_dict() for co in cos],
        'matrix': matrix
    })

@api_bp.route('/outcomes/<course_id>/matrix', methods=['PUT', 'POST'])
def update_copo_matrix(course_id):
    data = request.get_json() or {}
    mapping = data.get('mapping') or data.get('matrix') or {}
    for co_code, targets in mapping.items():
        co = CourseOutcome.query.filter_by(course_id=course_id, code=co_code).first()
        if not co:
            continue
        for target_code, level_val in targets.items():
            try:
                lvl = int(level_val) if level_val not in ('', None, '-') else 0
            except (ValueError, TypeError):
                lvl = 0
            m = CO_PO_Mapping.query.filter_by(course_id=course_id, outcome_code=co_code, target_code=target_code).first()
            if m:
                m.level = lvl
            elif lvl > 0:
                m = CO_PO_Mapping(
                    course_id=course_id,
                    outcome_id=co.id,
                    outcome_code=co_code,
                    target_code=target_code,
                    level=lvl
                )
                db.session.add(m)
    db.session.commit()
    # Trigger attainment recalculation
    calculate_course_attainment(course_id)
    return jsonify({'success': True, 'message': 'Matrix updated and attainment recalculated'})

# ==============================================================================
# STUDENT RECORDS, ATTENDANCE & MARKS APIS
# ==============================================================================
@api_bp.route('/students', methods=['GET', 'POST'])
def handle_students():
    course_id = request.args.get('course')
    if request.method == 'POST':
        data = request.get_json() or {}
        roll = (data.get('rollNo') or data.get('roll_no') or '').strip()
        name = (data.get('name') or '').strip()
        if not roll or not name:
            return jsonify({'error': 'Roll number and name are required'}), 400
        st = Student.query.filter_by(roll_no=roll).first()
        if st:
            return jsonify({'error': f'Student with roll number {roll} already exists'}), 400
        st = Student(
            roll_no=roll,
            name=name,
            email=data.get('email') or f"{roll.lower()}@bmu.edu.in",
            department=data.get('department', 'Computer Science & Engineering'),
            batch=data.get('batch', '2022'),
            semester=data.get('semester', 'Semester 5'),
            section=data.get('section', 'A'),
            is_demo_data=False
        )
        db.session.add(st)
        db.session.flush()
        if course_id:
            enrol = StudentEnrolment(student_id=st.id, course_id=course_id, status='Active')
            db.session.add(enrol)
        db.session.commit()
        return jsonify(st.to_dict()), 201

    if course_id:
        students = get_students_for_course(course_id)
    else:
        students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@api_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    st = Student.query.get(student_id)
    if not st:
        return jsonify({'error': 'Student not found'}), 404
    db.session.delete(st)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Student deleted successfully'})

@api_bp.route('/records/<course_id>/attendance', methods=['GET'])
def get_attendance(course_id):
    records = get_attendance_records(course_id)
    return jsonify([r.to_dict() for r in records])

@api_bp.route('/records/<course_id>/attendance/batch', methods=['POST'])
@api_bp.route('/attendance/<course_id>/batch', methods=['POST'])
def update_attendance_batch(course_id):
    data = request.get_json() or {}
    att_map = data.get('attendance') or {}
    updated_count = 0
    for st_id, attended_val in att_map.items():
        try:
            val = int(attended_val)
        except (ValueError, TypeError):
            continue

        student = None
        if isinstance(st_id, int) or (isinstance(st_id, str) and st_id.isdigit()):
            student = Student.query.get(int(st_id))
        if not student:
            student = Student.query.filter_by(roll_no=str(st_id)).first()
        if not student:
            continue

        att = AttendanceRecord.query.filter_by(course_id=course_id, student_id=student.id).first()
        if att:
            att.attended_classes = val
            att.update_status()
        else:
            att = AttendanceRecord(
                course_id=course_id,
                student_id=student.id,
                total_classes=16,
                attended_classes=val
            )
            att.update_status()
            db.session.add(att)
        updated_count += 1
    db.session.commit()
    return jsonify({'success': True, 'message': f'{updated_count} attendance records updated successfully'})

@api_bp.route('/attendance/<course_id>/session', methods=['POST'])
def record_session_attendance(course_id):
    data = request.get_json() or {}
    session_num = data.get('sessionNumber', 1)
    session_date = data.get('sessionDate', '')
    records_map = data.get('records') or data.get('attendance') or {}
    user_id = session.get('user', {}).get('id')

    updated_count = 0
    for st_id, status_val in records_map.items():
        student = None
        if isinstance(st_id, int) or (isinstance(st_id, str) and st_id.isdigit()):
            student = Student.query.get(int(st_id))
        if not student:
            student = Student.query.filter_by(roll_no=str(st_id)).first()
        if not student:
            continue

        att = AttendanceRecord.query.filter_by(course_id=course_id, student_id=student.id).first()
        if att:
            if str(status_val).upper() in ['P', 'PRESENT', '1', 'TRUE']:
                att.attended_classes = min(att.total_classes, att.attended_classes + 1)
            elif str(status_val).upper() in ['A', 'ABSENT', '0', 'FALSE']:
                att.attended_classes = max(0, att.attended_classes - 1)
            att.update_status()
            updated_count += 1

    log = AuditLog(
        user_id=user_id,
        action='SESSION_ATTENDANCE_RECORD',
        module='Attendance',
        details=f"Recorded Session #{session_num} attendance ({session_date}) for {updated_count} students in {course_id}."
    )
    db.session.add(log)
    db.session.commit()

    all_records = AttendanceRecord.query.filter_by(course_id=course_id).all()
    avg_att = round(sum(r.percentage for r in all_records) / len(all_records), 1) if all_records else 0.0
    shortages = sum(1 for r in all_records if r.percentage < 75.0)

    return jsonify({
        'success': True,
        'message': f'Session #{session_num} attendance recorded for {updated_count} students.',
        'averageAttendance': avg_att,
        'shortageCount': shortages
    })

@api_bp.route('/attendance/<course_id>/student/<student_identifier>', methods=['POST', 'PUT'])
def override_student_attendance(course_id, student_identifier):
    data = request.get_json() or {}
    attended = data.get('attendedClasses')
    total = data.get('totalClasses', 16)
    reason = data.get('reason', 'Administrative Override')
    user_id = session.get('user', {}).get('id')

    student = None
    if str(student_identifier).isdigit():
        student = Student.query.get(int(student_identifier))
    if not student:
        student = Student.query.filter_by(roll_no=str(student_identifier)).first()
    if not student:
        return jsonify({'success': False, 'error': f'Student {student_identifier} not found'}), 404

    att = AttendanceRecord.query.filter_by(course_id=course_id, student_id=student.id).first()
    if not att:
        att = AttendanceRecord(
            course_id=course_id,
            student_id=student.id,
            total_classes=int(total),
            attended_classes=int(attended) if attended is not None else 14
        )
        db.session.add(att)
    else:
        if attended is not None:
            att.attended_classes = int(attended)
        if total is not None:
            att.total_classes = int(total)

    att.update_status()

    log = AuditLog(
        user_id=user_id,
        action='ATTENDANCE_OVERRIDE',
        module='Attendance',
        details=f"Overrode attendance for {student.roll_no} ({student.name}) in {course_id}: {att.attended_classes}/{att.total_classes} ({att.percentage}%). Reason: {reason}"
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Attendance override saved for {student.roll_no}',
        'record': att.to_dict()
    })

@api_bp.route('/attendance/<course_id>/shortages', methods=['GET'])
def get_attendance_shortages(course_id):
    try:
        threshold = float(request.args.get('threshold', 75.0))
    except (ValueError, TypeError):
        threshold = 75.0

    records = AttendanceRecord.query.filter_by(course_id=course_id).all()
    shortages = [r for r in records if r.percentage < threshold]
    return jsonify({
        'courseId': course_id,
        'threshold': threshold,
        'shortageCount': len(shortages),
        'students': [r.to_dict() for r in shortages]
    })

@api_bp.route('/records/<course_id>/marks', methods=['GET'])
def get_marks(course_id):
    marks = get_marks_records(course_id)
    assessments = get_assessments_for_course(course_id)
    return jsonify({
        'marks': [m.to_dict() for m in marks],
        'assessments': [a.to_dict() for a in assessments]
    })

@api_bp.route('/records/<course_id>/marks/batch', methods=['POST'])
@api_bp.route('/marks/<course_id>/batch', methods=['POST'])
def update_marks_batch(course_id):
    data = request.get_json() or {}
    assessment_id = data.get('assessmentId')
    marks_map = data.get('marks') or {}

    asm = None
    if assessment_id:
        if str(assessment_id).isdigit():
            asm = Assessment.query.get(int(assessment_id))
        if not asm:
            asm = Assessment.query.filter_by(course_id=course_id, name=str(assessment_id)).first()
        if not asm:
            asm = Assessment.query.filter_by(course_id=course_id).first()

    if asm and isinstance(marks_map, dict):
        for st_id, marks_val in marks_map.items():
            try:
                val = float(marks_val)
            except (ValueError, TypeError):
                continue

            student = None
            if isinstance(st_id, int) or (isinstance(st_id, str) and st_id.isdigit()):
                student = Student.query.get(int(st_id))
            if not student:
                student = Student.query.filter_by(roll_no=str(st_id)).first()
            if not student:
                continue

            sm = StudentMark.query.filter_by(course_id=course_id, student_id=student.id, assessment_id=asm.id).first()
            if sm:
                sm.marks_obtained = val
                sm.is_weak_student = val < (0.40 * sm.max_marks)
            else:
                sm = StudentMark(
                    course_id=course_id,
                    student_id=student.id,
                    assessment_id=asm.id,
                    marks_obtained=val,
                    max_marks=asm.max_marks,
                    is_weak_student=val < (0.40 * asm.max_marks)
                )
                db.session.add(sm)
        db.session.commit()
        calculate_course_attainment(course_id)
        return jsonify({'success': True, 'message': 'Marks updated and attainment recalculated'})
    return jsonify({'success': False, 'error': 'Assessment not found or marks payload invalid'}), 400

# ==============================================================================
# OUTCOME ATTAINMENT API
# ==============================================================================
@api_bp.route('/attainment/<course_id>', methods=['GET', 'POST'])
def get_attainment(course_id):
    records = calculate_course_attainment(course_id)
    po_data = calculate_program_outcome_attainment(course_id)
    return jsonify({
        'records': [r.to_dict() for r in records],
        'poData': po_data
    })

# ==============================================================================
# GENERIC EXCEL DATA IMPORT APIS
# ==============================================================================
@api_bp.route('/import/inspect', methods=['POST'])
def import_inspect():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    f = request.files['file']
    file_bytes = f.read()
    res = inspect_excel_workbook(file_bytes)
    return jsonify(res)

@api_bp.route('/import/preview', methods=['POST'])
def import_preview():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    f = request.files['file']
    file_bytes = f.read()
    sheet_name = request.form.get('sheetName')
    header_row = int(request.form.get('headerRow', 10))
    res = preview_sheet_data(file_bytes, sheet_name, header_row=header_row)
    return jsonify(res)

@api_bp.route('/import/execute', methods=['POST'])
def import_execute():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    f = request.files['file']
    file_bytes = f.read()
    sheet_name = request.form.get('sheetName')
    course_id = request.form.get('courseId', 'CSE2724')
    header_row = int(request.form.get('headerRow', 10))
    data_start_row = int(request.form.get('dataStartRow', 12))
    overwrite = request.form.get('overwrite', 'false').lower() == 'true'
    mapping_str = request.form.get('columnMapping', '{}')
    try:
        column_mapping = json.loads(mapping_str)
    except Exception:
        column_mapping = {'roll_no': 2, 'name': 3}

    res = execute_excel_import(
        file_bytes=file_bytes,
        sheet_name=sheet_name,
        course_id=course_id,
        column_mapping=column_mapping,
        header_row=header_row,
        data_start_row=data_start_row,
        overwrite=overwrite
    )
    return jsonify(res)

# ==============================================================================
# SOFTWARE ENGINEERING CAPSTONE APIS (SRS, UML, TESTING, SPM)
# ==============================================================================
@api_bp.route('/se/requirements', methods=['GET', 'POST'])
def se_requirements():
    if request.method == 'POST':
        data = request.get_json() or {}
        req = ProjectRequirement(
            req_id=data.get('reqId'),
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category', 'Functional'),
            moscow=data.get('moscow', 'Must Have'),
            status=data.get('status', 'Implemented'),
            stakeholder=data.get('stakeholder', 'Faculty'),
            acceptance_criteria=data.get('acceptanceCriteria', '')
        )
        db.session.add(req)
        db.session.commit()
        return jsonify(req.to_dict()), 201

    moscow_filter = request.args.get('moscow')
    reqs = get_requirements(moscow_filter=moscow_filter)
    return jsonify([r.to_dict() for r in reqs])

@api_bp.route('/se/diagrams', methods=['GET'])
def se_diagrams():
    diagram_type = request.args.get('type')
    diagrams = get_architecture_diagrams(diagram_type=diagram_type)
    return jsonify([d.to_dict() for d in diagrams])

@api_bp.route('/se/testcases', methods=['GET', 'POST'])
def se_testcases():
    if request.method == 'POST':
        data = request.get_json() or {}
        tc = TestCase(
            test_id=data.get('testId'),
            module=data.get('module'),
            test_type=data.get('testType', 'System'),
            test_scenario=data.get('testScenario'),
            preconditions=data.get('preconditions'),
            test_inputs=data.get('testInputs'),
            expected_output=data.get('expectedOutput'),
            actual_output=data.get('actualOutput'),
            test_result=data.get('testResult', 'Pass'),
            severity=data.get('severity', 'Medium'),
            tester=data.get('tester', 'QA Engineer')
        )
        db.session.add(tc)
        db.session.commit()
        return jsonify(tc.to_dict()), 201

    data = get_test_management_data()
    return jsonify({
        'testCases': [t.to_dict() for t in data['testCases']],
        'metrics': data['metrics']
    })

@api_bp.route('/se/spm', methods=['GET'])
def se_spm():
    spm = get_spm_dashboard_data()
    return jsonify({
        'milestones': [m.to_dict() for m in spm['milestones']],
        'tasks': [t.to_dict() for t in spm['tasks']],
        'risks': [r.to_dict() for r in spm['risks']],
        'perts': [p.to_dict() for p in spm['perts']],
        'taskStats': spm['taskStats'],
        'cpmTotalDays': spm['cpmTotalDays']
    })

# ==============================================================================
# GOOGLE GEMINI AI COURSE HANDOUT SUMMARIZER
# ==============================================================================
@api_bp.route('/handouts/summarize', methods=['POST'])
def summarize_handout():
    """
    Module 7: Course Handout Summarizer with Google Gemini AI.
    Handles PDF/DOCX file upload or JSON payload with sample document reference.
    """
    file_bytes = None
    filename = None
    course_id = 'CSE2724'

    if 'file' in request.files:
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'Empty file submission'}), 400
        filename = file.filename
        file_bytes = file.read()
        course_id = request.form.get('courseId', 'CSE2724')
    elif request.is_json:
        data = request.get_json() or {}
        fname = data.get('fileName') or data.get('filename')
        course_id = data.get('courseId', 'CSE2724')
        if fname:
            filename = fname
            sample_path = os.path.join(current_app.root_path, 'static', 'sample_docs', fname)
            if not os.path.exists(sample_path):
                sample_path = os.path.join(current_app.root_path, 'static', 'sample_docs', 'CS301_Software_Engineering_Handout.pdf')
            try:
                with open(sample_path, 'rb') as f:
                    file_bytes = f.read()
            except Exception:
                file_bytes = b'%PDF-1.4 sample fallback'
    else:
        return jsonify({'success': False, 'error': 'No file uploaded or JSON payload provided'}), 400

    if not filename or not file_bytes or len(file_bytes) == 0:
        return jsonify({'success': False, 'error': 'Empty file or no file content available for summarization'}), 400

    allowed_exts = {'.pdf', '.docx'}
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed_exts:
        return jsonify({
            'success': False,
            'error': f"Unsupported file type: '{ext}'. Only PDF (.pdf) and Word documents (.docx) are permitted."
        }), 400

    if ext == '.pdf' and not file_bytes.startswith(b'%PDF-'):
        return jsonify({'success': False, 'error': 'Invalid or corrupted PDF file header'}), 400

    # Import gemini helper
    from services.ai_service import process_handout_with_gemini
    result = process_handout_with_gemini(file_bytes, ext, course_id, filename)
    return jsonify(result), (200 if result.get('success') else (429 if result.get('quota_exceeded') else 500))

# ==============================================================================
# COURSE FILE GENERATION
# ==============================================================================
@api_bp.route('/course-files/generate', methods=['POST'])
def generate_course_file():
    data = request.get_json() or {}
    course_id = data.get('courseId', 'CSE2724')
    course = get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'error': 'Course not found'}), 404

    return jsonify({
        'success': True,
        'message': f"Course File compiled successfully for {course.code} - {course.title}.",
        'courseId': course.id,
        'previewUrl': f"/course-file/preview?course={course.id}"
    })
