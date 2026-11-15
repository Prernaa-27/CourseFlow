"""
Generic Excel-Based Data Management & Import Engine
Parses, validates, and imports Maitri ERP dumps and custom OBE spreadsheets
into the CourseFlow PostgreSQL / SQLite database.
"""

import io
import openpyxl
from database import db
from models import Student, StudentEnrolment, StudentMark, Assessment

def inspect_excel_workbook(file_bytes):
    """
    Inspects an uploaded Excel file and returns metadata:
    sheet names, estimated row counts, and sample headers.
    """
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    except Exception as e:
        return {'success': False, 'error': f"Failed to read Excel workbook: {str(e)}"}

    sheets_meta = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        # Find potential header row (usually row 1, 10, or 11 in Maitri sheets)
        header_candidates = []
        for r in range(1, min(16, ws.max_row + 1)):
            row_vals = [str(ws.cell(r, c).value).strip() for c in range(1, min(15, ws.max_column + 1)) if ws.cell(r, c).value is not None]
            if any('roll' in v.lower() or 'student' in v.lower() or 'sr' in v.lower() for v in row_vals):
                header_candidates.append({'row': r, 'headers': row_vals})

        sample_rows = []
        for r in range(1, min(6, ws.max_row + 1)):
            vals = [str(ws.cell(r, c).value) if ws.cell(r, c).value is not None else '' for c in range(1, min(10, ws.max_column + 1))]
            if any(vals):
                sample_rows.append(vals)

        sheets_meta.append({
            'name': sheet_name,
            'maxRows': ws.max_row,
            'maxCols': ws.max_column,
            'headerCandidates': header_candidates,
            'sampleRows': sample_rows
        })

    return {
        'success': True,
        'sheetCount': len(wb.sheetnames),
        'sheets': sheets_meta
    }

def preview_sheet_data(file_bytes, sheet_name, header_row=10, limit=5):
    """
    Provides a preview of columns and records for a selected sheet.
    Infers potential mappings to Student and Assessment fields.
    """
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        if sheet_name not in wb.sheetnames:
            return {'success': False, 'error': f"Sheet '{sheet_name}' not found."}
        ws = wb[sheet_name]
    except Exception as e:
        return {'success': False, 'error': str(e)}

    # Extract headers
    headers = []
    for c in range(1, ws.max_column + 1):
        val = ws.cell(header_row, c).value
        headers.append({
            'colIndex': c,
            'colLetter': openpyxl.utils.get_column_letter(c),
            'header': str(val).strip() if val is not None else f"Column {c}"
        })

    # Read preview records
    preview_rows = []
    start_row = header_row + 1
    # Check if row header_row+1 has 'Out of(30)' max marks
    first_data_val = str(ws.cell(start_row, 2).value or '')
    if 'out of' in first_data_val.lower() or ws.cell(start_row, 1).value is None:
        start_row += 1

    for r in range(start_row, min(start_row + limit, ws.max_row + 1)):
        row_dict = {}
        for h in headers:
            v = ws.cell(r, h['colIndex']).value
            row_dict[h['header']] = v if v is not None else ''
        if any(str(v).strip() for v in row_dict.values()):
            preview_rows.append(row_dict)

    return {
        'success': True,
        'sheetName': sheet_name,
        'headerRow': header_row,
        'dataStartRow': start_row,
        'headers': headers,
        'previewRows': preview_rows,
        'totalEstimatedRows': max(0, ws.max_row - start_row + 1)
    }

def execute_excel_import(file_bytes, sheet_name, course_id, column_mapping, header_row=10, data_start_row=12, overwrite=False):
    """
    Executes database import with transactional integrity and validation.
    column_mapping: dict mapping internal field keys to Excel column indices or headers:
      {
        'roll_no': 2,        # Col B
        'name': 3,           # Col C
        'assessments': {
           'ASM_ID_1': 4,    # Col D
           'ASM_ID_2': 5,    # Col E
        }
      }
    """
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        if sheet_name not in wb.sheetnames:
            return {'success': False, 'error': f"Sheet '{sheet_name}' not found."}
        ws = wb[sheet_name]
    except Exception as e:
        return {'success': False, 'error': str(e)}

    roll_col = int(column_mapping.get('roll_no', 2))
    name_col = int(column_mapping.get('name', 3))
    asm_map = column_mapping.get('assessments', {})  # { assessment_id: col_index }

    # Validate assessments exist in course
    valid_asms = {a.id: a for a in Assessment.query.filter_by(course_id=course_id).all()}

    imported_count = 0
    skipped_count = 0
    rejected_count = 0
    error_report = []

    for r in range(data_start_row, ws.max_row + 1):
        roll_raw = ws.cell(r, roll_col).value
        name_raw = ws.cell(r, name_col).value

        if roll_raw is None and name_raw is None:
            continue

        if not roll_raw:
            rejected_count += 1
            error_report.append({'row': r, 'roll': 'N/A', 'name': str(name_raw or ''), 'error': 'Missing roll number.'})
            continue

        roll = str(roll_raw).strip()
        name = str(name_raw or '').strip() or f"Student {roll}"

        # Duplicate check within this course
        st = Student.query.filter_by(roll_no=roll).first()
        is_new_student = False
        if not st:
            st = Student(
                roll_no=roll,
                name=name,
                email=f"{roll.lower()}@bmu.edu.in",
                department="Computer Science & Engineering",
                is_demo_data=False
            )
            db.session.add(st)
            db.session.flush()
            is_new_student = True
        else:
            if not overwrite and StudentEnrolment.query.filter_by(student_id=st.id, course_id=course_id).first():
                skipped_count += 1
                error_report.append({
                    'row': r,
                    'roll': roll,
                    'name': name,
                    'error': 'Student already enrolled in this course (Overwrite is OFF).'
                })
                continue
            elif overwrite:
                st.name = name

        # Ensure Enrolment
        enrol = StudentEnrolment.query.filter_by(student_id=st.id, course_id=course_id).first()
        if not enrol:
            enrol = StudentEnrolment(student_id=st.id, course_id=course_id, status='Active')
            db.session.add(enrol)

        # Marks validation & storage
        row_has_error = False
        row_marks = []
        for asm_id_str, col_idx in asm_map.items():
            asm_id = int(asm_id_str) if str(asm_id_str).isdigit() else asm_id_str
            asm_obj = valid_asms.get(asm_id)
            if not asm_obj:
                continue

            val_raw = ws.cell(r, int(col_idx)).value
            if val_raw is None or val_raw == '':
                val = 0.0
            else:
                try:
                    val = float(val_raw)
                except ValueError:
                    rejected_count += 1
                    error_report.append({
                        'row': r,
                        'roll': roll,
                        'name': name,
                        'error': f"Non-numeric mark '{val_raw}' for assessment '{asm_obj.name}'"
                    })
                    row_has_error = True
                    break

            # Validate against max marks
            if val < 0.0 or val > asm_obj.max_marks:
                rejected_count += 1
                error_report.append({
                    'row': r,
                    'roll': roll,
                    'name': name,
                    'error': f"Marks ({val}) out of bounds [0.0 - {asm_obj.max_marks}] for '{asm_obj.name}'"
                })
                row_has_error = True
                break

            row_marks.append((asm_obj, val))

        if row_has_error:
            # Skip storing marks for this rejected row
            continue

        # Save valid marks
        for asm_obj, val in row_marks:
            sm = StudentMark.query.filter_by(student_id=st.id, assessment_id=asm_obj.id).first()
            if not sm:
                sm = StudentMark(
                    course_id=course_id,
                    student_id=st.id,
                    assessment_id=asm_obj.id,
                    marks_obtained=val,
                    max_marks=asm_obj.max_marks,
                    is_weak_student=val < (0.40 * asm_obj.max_marks)
                )
                db.session.add(sm)
            else:
                sm.marks_obtained = val
                sm.is_weak_student = val < (0.40 * asm_obj.max_marks)

        imported_count += 1

    db.session.commit()

    # Automatically trigger attainment recalculation for this course
    from services.attainment_service import calculate_course_attainment
    calculate_course_attainment(course_id)

    return {
        'success': True,
        'courseId': course_id,
        'sheetName': sheet_name,
        'importedCount': imported_count,
        'skippedCount': skipped_count,
        'rejectedCount': rejected_count,
        'totalProcessed': imported_count + skipped_count + rejected_count,
        'errorReport': error_report
    }
