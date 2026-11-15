# CourseFlow (CFMS) – Detailed Technical & Architecture Reference

**System:** CourseFlow – Course File Management System  
**Framework:** Flask 3.1.2 / SQLAlchemy 2.0 / Python 3.13  
**Database:** Relational SQLite with PostgreSQL Schema Compatibility  
**Target Environment:** BML Munjal University Accreditation Engine  

---

## 1. System Architecture

CourseFlow follows a clean 3-tier Layered Architecture:

```
+-------------------------------------------------------------------+
|                        PRESENTATION LAYER                         |
|  - Jinja2 HTML Templates (Bootstrap 5.3, Bootstrap Icons)         |
|  - Vanilla ES6 JavaScript Controllers (app.js, records.js, etc.)  |
|  - Chart.js 4.4 Data Visualizations                               |
+---------------------------------+---------------------------------+
                                  | HTTP / JSON REST APIs
+---------------------------------v---------------------------------+
|                         BUSINESS LAYER                            |
|  - Blueprints: auth_bp, course_bp, academic_bp, curriculum_bp,    |
|    admin_bp, api_bp, engineering_bp                               |
|  - Domain Services:                                               |
|    * course_service.py (25-section tracking & completion metrics) |
|    * student_service.py (Attendance, marks, student enrolments)   |
|    * curriculum_service.py (Syllabus units, session planning)     |
|    * attainment_service.py (NBA direct/indirect OBE formulas)     |
|    * excel_import_service.py (openpyxl parsing & mapping)         |
|    * gemini_service.py (Google Gemini GenAI summarization)        |
+---------------------------------+---------------------------------+
                                  | SQLAlchemy ORM
+---------------------------------v---------------------------------+
|                       PERSISTENCE LAYER                           |
|  - SQLite (courseflow.db) / Hosted PostgreSQL Compatible          |
|  - 17 Relational Entities with Foreign Keys & Cascade Constraints |
|  - AuditLog Transaction Ledger                                    |
+-------------------------------------------------------------------+
```

---

## 2. Relational Database Schema & Entities

The system defines 17 relational database models in the `models/` directory:

1. **`User` (`users`):** Stores credentials, hashed passwords, roles (`faculty`, `admin`), and department.
2. **`Course` (`courses`):** Master course definition (`code`, `title`, `credits`, `semester`, `status`, `coordinator_id`).
3. **`CourseFileSection` (`course_file_sections`):** Represents each of the 25 official sections with `section_number` (1–25), `status`, `notes`, `updated_at`, `updated_by_id`.
4. **`CourseDocument` (`course_documents`):** File attachments archived for course file sections (`file_name`, `file_path`, `file_type`, `file_size_bytes`).
5. **`Student` (`students`):** Master student record (`roll_no`, `name`, `email`, `batch`, `section`, `is_demo_data`).
6. **`StudentEnrolment` (`student_enrolments`):** Many-to-many relationship linking students to courses.
7. **`Assessment` (`assessments`):** Assessment definitions (`name`, `assessment_type`, `weightage_percent`, `max_marks`, `mapped_cos`).
8. **`AssessmentComponent` (`assessment_components`):** Sub-components of continuous evaluation.
9. **`StudentMark` (`student_marks`):** Evaluated marks obtained per student per assessment with automatic $<40\%$ weak student flagging (`is_weak_student`).
10. **`AttendanceRecord` (`attendance_records`):** Cumulative attendance records (`total_classes`, `attended_classes`, `percentage`, `status`, `is_shortage`).
11. **`CourseOutcome` (`course_outcomes`):** Accredited outcomes with Bloom's taxonomy mapping.
12. **`CO_PO_Mapping` (`co_po_mappings`):** Correlation strength (1: Low, 2: Moderate, 3: High) between COs and POs/PSOs.
13. **`COAttainmentRecord` (`co_attainment_records`):** Persisted outcome attainment percentages and levels.
14. **`SyllabusModule` (`syllabus_modules`):** Modules extracted from course handouts.
15. **`SessionPlan` (`session_plans`):** Detailed lecture-by-lecture session delivery schedule.
16. **`StudentFeedback` (`student_feedback`):** Course evaluation survey responses.
17. **`AuditLog` (`audit_logs`):** Transaction audit logging with `user_id`, `action`, `module`, `details`, and `timestamp`.

---

## 3. Outcome-Based Education (OBE) Mathematical Formulas

### Direct Course Outcome Attainment
In accordance with NBA Tier-1 guidelines, a student attains a Course Outcome if they score $\ge 40\%$ of the maximum marks allocated to that outcome:

$$\text{Attainment } \% = \frac{\text{Students scoring } \ge 40\%}{\text{Total Evaluated Students}} \times 100$$

Attainment levels are assigned based on institutional targets:
- **Level 1 (Low):** $50.0\% \le \text{Attainment } < 60.0\%$
- **Level 2 (Moderate):** $60.0\% \le \text{Attainment } < 70.0\%$
- **Level 3 (High):** $\text{Attainment } \ge 70.0\%$

For `CSE2724`:
- **CO1:** $385 / 391 = 98.47\% \implies \text{Level 3 (High)}$
- **CO2:** $385 / 391 = 98.47\% \implies \text{Level 3 (High)}$
- **CO3:** $372 / 391 = 95.14\% \implies \text{Level 3 (High)}$

### Program Outcome (PO) Correlation Attainment
Program Outcome attainment is calculated by weighting each Course Outcome's attainment level against its correlation value in the articulation matrix:

$$PO_j = \frac{\sum_{i=1}^{n} (\text{AttainmentLevel}(CO_i) \times \text{Corr}(CO_i, PO_j))}{\sum_{i=1}^{n} \text{Corr}(CO_i, PO_j)}$$

### Unmapped PO Omission Logic
If $\sum_{i=1}^{n} \text{Corr}(CO_i, PO_j) = 0$, the outcome is unmapped. To prevent misleading zero-value lines on radar and bar charts, unmapped POs are omitted:
```python
if total_weight > 0:
    mapped_pos.append({
        'code': po.code,
        'name': po.title,
        'attainment': round(weighted_sum / total_weight, 2),
        'correlation': round(total_weight / len(outcomes), 2)
    })
# Unmapped POs with total_weight == 0 are excluded from mapped_pos
```

---

## 4. Key REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/courses` | Lists all registered university courses with completion status |
| `GET` | `/api/students?course=<id>` | Lists enrolled students with pagination and search |
| `GET` | `/api/records/<id>/marks` | Returns all 1,173 evaluated marks and assessment definitions |
| `POST` | `/api/records/<id>/marks/batch` | Persists edited marks and recalculates attainment |
| `GET` | `/api/records/<id>/attendance` | Returns attendance records with percentage and shortage status |
| `POST` | `/api/attendance/<id>/session` | Records session-wise attendance with date and session number |
| `POST` | `/api/attendance/<id>/student/<rollNo>` | Overrides individual student attendance with audit reason |
| `GET` | `/api/attendance/<id>/shortages` | Queries students falling below configurable threshold (default 75%) |
| `GET` | `/api/attainment/<id>` | Computes real-time Direct, Indirect, and PO attainment |
| `POST` | `/api/outcomes/<id>/matrix` | Persists updated CO-PO correlation matrix |
| `GET` | `/api/course-files/<id>/sections` | Returns status and evidence details for all 25 sections |
| `POST` | `/api/course-files/<id>/sections/<num>/upload` | Uploads evidence document and updates compliance notes |
| `POST` | `/api/handouts/summarize` | Extracts syllabus modules using Google Gemini GenAI |
