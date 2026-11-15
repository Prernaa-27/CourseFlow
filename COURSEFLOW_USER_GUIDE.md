# CourseFlow (CFMS) – User & Evaluation Demonstration Guide

**Project:** CourseFlow – University Course File Management System  
**Institution:** BML Munjal University (School of Engineering & Technology)  
**Primary Course:** Human Computer Interaction (`CSE2724`)  
**Target Audience:** Faculty Evaluators, Students, and External Accreditation Auditors  

---

## 1. Quick Start & Credentials

CourseFlow includes two authenticated roles with strict separation:

| User Role | Username / Email | Password | Access Rights |
|---|---|---|---|
| **Faculty (Course Coordinator)** | `faculty@courseflow.demo` | `courseflow123` | Full access to primary course CSE2724, 25-section dossier, marks, attendance, syllabus, and AI summarizer. |
| **Academic Administrator** | `admin@courseflow.demo` | `courseflow123` | Department-level dashboard, faculty directory, workload assignment, and multi-course audit monitoring. |

> [!NOTE]
> In compliance with security directives, role switching is forbidden from the top navigation bar. Users must log in via `/login` with their respective credentials.

---

## 2. Navigating the 8 Core Modules

### Module 1: Dashboard (`/dashboard`)
- **Primary Course Display:** Automatically opens with `CSE2724` (Human Computer Interaction).
- **Executive Metrics:** Displays 391 enrolled students, 99.49% pass rate, 25 course file sections, and 89.8% average attendance.
- **Shortage Monitor Alert:** Prominently highlights 10 students with synthesized attendance $<75\%$ and links to remedial action.

### Module 2: Course Management (`/courses` & `/courses/<id>`)
- **Course Portfolio:** Displays department courses (`CSE2724`, `CSE3005`, `CS302`, `CS303`, `CS401`, `CS202`).
- **Syllabus Planning (`/syllabus`):** Browse 5 approved units, 45 teaching hours, and mapped Bloom's taxonomy outcomes.
- **Session Planner (`/session-planner`):** Review chronological lecture and lab schedule.

### Module 3: Student Management (`/students`)
- **391 Authentic HCI Records:** Imported from `CSE2724.xlsx` (Clean Maitri Data).
- **Search & Filter:** Real-time search by roll number (e.g. `230C2030010`) or student name.
- **Data Transparency Note:** Explains that records for `CSE2724` are authentic university enrolments, while `CSE3005` records are demonstration samples.

### Module 4: Academic Records (`/marks`, `/attendance`, `/feedback`)
- **Marks Register (`/marks`):**
  - Switch between components: **Lab Assessment (30)**, **Project (30)**, and **End-Term Examination (40)**.
  - Interactive mark inputs validate that values never exceed maximum component marks or drop below 0.
  - Batch Save persists scores directly into SQLite and dynamically triggers attainment recalculation.
- **Attendance Management (`/attendance`):**
  - Clearly tagged with `SAMPLE / DEMO DATA (SYNTHESIZED)` badge.
  - Record session presence using **P** / **A** toggle switches.
  - "Mark All Present" and "Mark All Absent" one-click bulk tools.
  - Live `< 75%` shortage counter dynamically flags students requiring compensatory labs.
- **Feedback Module (`/feedback`):**
  - Analyzes student feedback on Figma labs, interaction design heuristics, and usability testing.

### Module 5: Outcomes & CO-PO Mapping (`/outcomes`)
- **Accredited CO Formulations:** CO1 (Design principles), CO2 (Wireframing & Figma prototyping), CO3 (Usability evaluation & heuristic inspection).
- **Correlation Matrix:** Editable matrix mapping COs to PO1–PO12 and PSO1–PSO4 on 1–3 scale.
- **Dynamic Recalculation:** Saving the matrix automatically updates weighted average correlations in real time.

### Module 6: Attainment Analytics (`/attainment`)
- **Direct Attainment Ledger:** Compares student performance against the 70.0% benchmark. Direct attainment achieved Level 3 (CO1: 98.5%, CO2: 98.5%, CO3: 95.1%).
- **PO/PSO Attainment Bar Chart:** Shows outcome attainment levels on a 3.0 scale.
- **Zero-Value Mini-Line Elimination:** Unmapped outcomes (PO6, PO8, PO9, PO12) are omitted from the visualization.

### Module 7: AI Handout Assistant (`/ai-assistant`)
- **Gemini-Powered Analysis:** Upload any course syllabus (PDF or DOCX) or click **Load Sample Handout**.
- **Interactive File Controls:** Select, inspect, and remove files using the **Remove** button.
- **Faculty Review & Commit:** Review identified modules and suggested COs before clicking **Approve & Update Syllabus**.

### Module 8: Course File Management & Dossier (`/course-file` & `/course-file/preview`)
- **25 Official Sections:** Matches BML Munjal University `Course File Template.pdf`.
- **Evidence Upload Modal:** Click **Edit** on any section to update audit compliance notes, change status, and upload supporting PDF/DOCX files.
- **Audit-Ready Preview:** Click **Preview Handout** to view the full dossier with one-click print styling.

---

## 3. Recommended Faculty Viva Walkthrough Script (5 Minutes)

1. **Minute 1 – Overview & Architecture:**
   - Log in as `faculty@courseflow.demo`.
   - Show that the dashboard defaults to **Human Computer Interaction (CSE2724)** with **391 authentic students**.
   - Point out the **99.49% pass rate** and explain the 2 failed students out of 391.
2. **Minute 2 – Academic Records & Attendance Transparency:**
   - Open `/attendance`. Note the `SAMPLE / DEMO DATA (SYNTHESIZED)` badge.
   - Show how changing a student's session status updates their cumulative percentage and triggers the shortage alert.
   - Open `/marks`. Show how 1,173 authentic marks from `CSE2724.xlsx` are bound to Lab (30), Project (30), and SEE (40).
3. **Minute 3 – Outcome-Based Education (OBE) Calculations:**
   - Open `/outcomes` and `/attainment`.
   - Explain the attainment formula: Direct (80%) + Indirect (20%).
   - Show that PO6, PO8, PO9, and PO12 have correlation 0 and are excluded from charts to prevent misleading zero-value lines.
4. **Minute 4 – 25 Official Sections & Evidence Management:**
   - Open `/course-file`. Show all 25 sections matching BMU guidelines.
   - Click **Edit** on Section 13 (Mid-Semester Papers) and upload an evidence file.
5. **Minute 5 – One-Click Dossier Compilation:**
   - Click **Preview Handout** (`/course-file/preview`).
   - Scroll through the 25 sections and click **Print / Export PDF**.
