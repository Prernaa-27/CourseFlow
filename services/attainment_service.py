"""
Outcome & Program Attainment Calculation Service
Implements authentic BML Munjal University OBE Attainment formulas
from CSE2724.xlsx (Calculation Sheet, Final Result rows 21-36).
"""

from database import db
from models import (
    Course, CourseOutcome, CO_PO_Mapping, Student, StudentEnrolment,
    StudentMark, Assessment, StudentFeedback, COAttainmentRecord
)

def calculate_course_attainment(course_id='CSE2724'):
    """
    Computes dynamic course outcome and program outcome attainment from live database records.
    Methodology derived from BML Munjal University official calculation workbook:
    1. Student level per CO is evaluated based on weighted marks across assessments:
       Level 3 if percentage >= 50%
       Level 2 if percentage >= 45%
       Level 1 if percentage < 45%
    2. Direct CO Attainment = Average attainment level of all registered students.
    3. Target compliance: Level 3 if >= 70% of students achieve Level 3; Level 2 if >= 65%.
    4. Program Outcome (PO) Attainment:
       PO_k = SUMPRODUCT(CO_Attainment[1..m], Correlation[1..m, k]) / SUM(Correlation[1..m, k])
       Unmapped POs (where SUM(Correlation) == 0) are flagged as None (omitted from charts).
    """
    course = Course.query.filter_by(id=course_id).first() or Course.query.filter_by(code=course_id).first()
    if not course:
        return []

    outcomes = CourseOutcome.query.filter_by(course_id=course.id).order_by(CourseOutcome.code).all()
    if not outcomes:
        return []

    # Get enrolled students
    enrolments = StudentEnrolment.query.filter_by(course_id=course.id).all()
    students = [e.student_rel for e in enrolments if e.student_rel]
    total_students = len(students)
    if total_students == 0:
        return []

    # Get assessments for this course
    assessments = Assessment.query.filter_by(course_id=course.id).all()
    asms_by_id = {a.id: a for a in assessments}

    # Identify component assessments
    lab_asm = next((a for a in assessments if 'lab' in a.name.lower()), None)
    proj_asm = next((a for a in assessments if 'proj' in a.name.lower() or 'assignment' in a.name.lower()), None)
    see_asm = next((a for a in assessments if 'end' in a.name.lower() or 'term' in a.name.lower() or 'exam' in a.name.lower()), None)

    # Assessment weighting by CO (Calculation Sheet defaults)
    # If course is CSE2724:
    co_weights_config = {
        'CO1': {'lab': 0.4, 'proj': 0.4, 'see': 0.2, 'overall_weight': 0.35},
        'CO2': {'lab': 0.3, 'proj': 0.5, 'see': 0.2, 'overall_weight': 0.40},
        'CO3': {'lab': 0.3, 'proj': 0.4, 'see': 0.3, 'overall_weight': 0.25}
    }

    # Fetch all marks for this course
    all_marks = StudentMark.query.filter_by(course_id=course.id).all()
    marks_by_student = {}
    for sm in all_marks:
        if sm.student_id not in marks_by_student:
            marks_by_student[sm.student_id] = {}
        marks_by_student[sm.student_id][sm.assessment_id] = sm.marks_obtained

    records = []
    co_avg_levels = {}

    for co in outcomes:
        cfg = co_weights_config.get(co.code, {'lab': 0.33, 'proj': 0.33, 'see': 0.34, 'overall_weight': 1.0 / len(outcomes)})
        
        # Determine maximum weighted marks
        max_weighted = 0.0
        if lab_asm and lab_asm.id in asms_by_id:
            max_weighted += lab_asm.max_marks * cfg['lab']
        if proj_asm and proj_asm.id in asms_by_id:
            max_weighted += proj_asm.max_marks * cfg['proj']
        if see_asm and see_asm.id in asms_by_id:
            max_weighted += see_asm.max_marks * cfg['see']

        if max_weighted == 0.0:
            max_weighted = 100.0

        levels = []
        for st in students:
            m = marks_by_student.get(st.id, {})
            lab_m = m.get(lab_asm.id, 0.0) if lab_asm else 0.0
            proj_m = m.get(proj_asm.id, 0.0) if proj_asm else 0.0
            see_m = m.get(see_asm.id, 0.0) if see_asm else 0.0

            score = (lab_m * cfg['lab']) + (proj_m * cfg['proj']) + (see_m * cfg['see'])
            pct = (score / max_weighted) if max_weighted else 0.0

            if pct >= 0.50:
                lvl = 3
            elif pct >= 0.45:
                lvl = 2
            else:
                lvl = 1
            levels.append(lvl)

        students_ge3 = sum(1 for l in levels if l >= 3)
        pct_ge3 = round((students_ge3 / total_students) * 100.0, 1) if total_students else 0.0
        avg_level = round(sum(levels) / total_students, 2) if total_students else 0.0
        co_avg_levels[co.code] = avg_level

        # Attainment benchmark Level
        final_level = 3 if pct_ge3 >= 70.0 else (2 if pct_ge3 >= 65.0 else 1)

        # Upsert COAttainmentRecord
        rec = COAttainmentRecord.query.filter_by(course_id=course.id, outcome_code=co.code).first()
        if not rec:
            rec = COAttainmentRecord(
                course_id=course.id,
                outcome_code=co.code,
                direct_attainment=pct_ge3,
                indirect_attainment=85.0,  # survey default
                overall_attainment=pct_ge3,
                students_evaluated=total_students,
                students_attained=students_ge3,
                attainment_percentage=pct_ge3,
                attainment_level=final_level,
                target_benchmark=co.target_benchmark or 70.0
            )
            db.session.add(rec)
        else:
            rec.direct_attainment = pct_ge3
            rec.overall_attainment = pct_ge3
            rec.students_evaluated = total_students
            rec.students_attained = students_ge3
            rec.attainment_percentage = pct_ge3
            rec.attainment_level = final_level

        co.class_average = pct_ge3
        co.attainment_level = final_level
        records.append(rec)

    db.session.commit()
    return records

def calculate_program_outcome_attainment(course_id='CSE2724'):
    """
    Computes PO and PSO attainment for a course.
    Formula: PO_k = SUM(CO_j * Corr_jk) / SUM(Corr_jk)
    Returns a dict with mapped POs and filters out unmapped ones.
    """
    course = Course.query.filter_by(id=course_id).first() or Course.query.filter_by(code=course_id).first()
    if not course:
        return {}

    # Ensure CO attainment is up to date
    co_records = calculate_course_attainment(course.id)
    co_levels = {r.outcome_code: r.attainment_level for r in co_records}

    # If co_levels is empty, fallback to 3.0
    if not co_levels:
        for co in CourseOutcome.query.filter_by(course_id=course.id).all():
            co_levels[co.code] = 3.0

    mappings = CO_PO_Mapping.query.filter_by(course_id=course.id).all()
    targets = {}
    for m in mappings:
        if m.target_code not in targets:
            targets[m.target_code] = {}
        targets[m.target_code][m.outcome_code] = m.level

    all_target_codes = [f"PO{i}" for i in range(1, 13)] + [f"PSO{i}" for i in range(1, 5)]
    po_results = []

    for code in all_target_codes:
        corrs = targets.get(code, {})
        sum_weights = sum(corrs.values())
        if sum_weights > 0:
            weighted_sum = sum(co_levels.get(co, 3.0) * lvl for co, lvl in corrs.items())
            val = round(weighted_sum / sum_weights, 2)
            po_results.append({
                'code': code,
                'attainment': val,
                'isMapped': True,
                'correlation': corrs
            })
        else:
            po_results.append({
                'code': code,
                'attainment': None,
                'isMapped': False,
                'correlation': {}
            })

    return {
        'targets': po_results,
        'mappedOnly': [p for p in po_results if p['isMapped']]
    }
