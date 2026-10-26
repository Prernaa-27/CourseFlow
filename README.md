# CourseFlow - Course File Management System (CFMS)

**CourseFlow** is a university Course File Management System (CFMS) developed as a Software Engineering course project. It provides faculty members and department administrators with a clean, structured, and easy-to-explain web application to manage syllabus planning, student records, assessments, attendance, course outcomes, and course dossiers.

---

## 1. System Scope & Core Features

The project is intentionally scoped and simplified so engineering students can easily understand, maintain, test, and defend every feature during a laboratory viva:

### A. Authentication & Role-Specific Dashboards
- **Demo Logins**: Dedicated one-click credentials for **Faculty** (`faculty@courseflow.demo`) and **Administrator** (`admin@courseflow.demo`).
- **Dynamic Dashboard**:
  - **Faculty View**: Displays assigned active courses, syllabus completion progress, timetable lectures for today, and quick actions.
  - **Administrator View**: Displays department metrics (5 faculty, 5 courses, completed files), course allocations table, and administrative tools.
- **Demo Role Switcher**: Instant switching between Faculty and Admin roles directly from the top navigation bar without manual logout.

### B. Course Management
- Catalog of departmental courses (CS301, CS302, CS303, CS401, CS202).
- Add new course modal with validation.
- Search courses by code or title, with real-time status badges (*Completed*, *In Progress*, *Draft*).
- Course details page with syllabus overview and quick links.

### C. Syllabus & Session Planning
- **Syllabus Units**: Add, edit, and delete syllabus units with module titles, topics covered, teaching hours, and review status.
- **Teaching Session Planner**: Add, edit, and track lecture delivery dates, topics, teaching methods (Chalk & Talk, Slide Deck, Code Demo, Case Study), and completion status.

### D. Student Records & Academic Assessments
- **Student Roster**: Add and view student records (Roll Number, Name, Email, Semester).
- **Marks Register**: Enter student assessment marks with immediate percentage calculation:
  $$\text{Percentage} = \left(\frac{\text{Marks Obtained}}{\text{Maximum Marks}}\right) \times 100$$
- **Attendance Tracker**: Binary attendance marking (**Present `P`** / **Absent `A`**) with individual student percentages, bulk "Mark All Present" / "Mark All Absent", and $<75\%$ low-attendance warning badges.
- **Interactive Feedback**: Submit 1 to 5-star course ratings with optional student feedback comments, automatically updating the course rating distribution and average score.

### E. CO-PO Outcome Mapping & Attainment Analytics
- **Articulation Matrix**: Map Course Outcomes (CO1–CO5) to Program Outcomes (PO1–PO12) and PSOs using a straightforward scale:
  - `0`: Unmapped (No correlation)
  - `1`: Low (Slight)
  - `2`: Moderate (Medium)
  - `3`: High (Substantial)
- **Outcome Attainment**: Transparent comparison between student marks and target benchmarks (e.g. 75%), rendered with clean Chart.js bar visualizations and difference indicators.

### F. Course Handout Summarizer (Demo Simulation Mode)
- Upload syllabus documents (PDF, DOCX, TXT) or click **Load Sample Handout** for immediate testing.
- Transparently demonstrates document parsing and outcome generation using structured demo data without requiring external paid AI keys.
- **Faculty Review Step**: Allows faculty to review and edit extracted summaries before approving them.

### G. Course File Dossier
- Tracks the **8 Essential Sections** of a university course file:
  1. *Course Information & Objectives*
  2. *Syllabus Units & Topics*
  3. *Teaching Session Plans*
  4. *Student Records & Enrollment*
  5. *Assessments & Marks Register*
  6. *Attendance Records*
  7. *Student Feedback Summary*
  8. *CO-PO Outcome Mapping*
- **Real-Time Readiness**: Calculates completion percentage directly from the 8 checked items:
  $$\text{Completion \%} = \text{round}\left(\frac{\text{Completed Sections}}{8} \times 100\right)$$
- **Dossier Preview & Export**: Preview the entire combined course portfolio and print or save as PDF using the browser's native print interface (`window.print()`).

### H. Administrator Management
- Faculty member roster with email, department, and teaching load.
- Course catalog management and teaching allocations.
- Department-level course-file completion monitoring with CSV export.

---

## 2. Technology Stack

- **Backend**: Python 3 with Flask 3.x (Modular routing, Jinja2 template inheritance, REST contracts)
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), CSS3 with custom CSS design tokens
- **UI Framework**: Bootstrap 5.3.3 (Responsive layout, modals, dropdowns)
- **Icons**: Bootstrap Icons 1.11.3
- **Charts**: Chart.js 4.4.2 (Responsive bar and progress charts)
- **Typography**: Google Fonts Inter
- **Testing**: Pytest automated test suite

> **No Heavy Frameworks**: No React, Vue, Angular, Next.js, TypeScript, Tailwind, or Node.js build tools. The project runs out-of-the-box on standard Python with zero build steps.

---

## 3. Project Directory Structure

```text
CourseFlow/
├── app.py                      # Flask server, page routes, and API endpoints
├── requirements.txt            # Python dependencies (Flask, pytest)
├── README.md                   # Project documentation & viva guide
├── templates/                  # Server-rendered Jinja2 HTML templates
│   ├── base.html               # Shared layout (sidebar, topbar, modals, scripts)
│   ├── login.html              # Login screen with quick demo role buttons
│   ├── dashboard.html          # Dynamic Faculty & Admin dashboards
│   ├── courses.html            # Course catalog with search & filters
│   ├── course_detail.html      # Course overview hub
│   ├── syllabus.html           # Syllabus units & contact hours
│   ├── session_planner.html    # Teaching session delivery log
│   ├── students.html           # Student roster & section filters
│   ├── assessments.html        # Evaluation components & weightages
│   ├── marks.html              # Marks entry ledger & percentage calculations
│   ├── attendance.html         # Binary Present/Absent attendance tracker
│   ├── feedback.html           # Interactive student feedback & star rating form
│   ├── outcomes.html           # 0-3 CO-PO mapping matrix
│   ├── attainment.html         # Attainment analytics & benchmark comparisons
│   ├── ai_assistant.html       # Handout summarizer (Demo simulation mode)
│   ├── course_file.html        # 8-section course file checklist
│   ├── course_file_preview.html# Complete printable course dossier
│   ├── admin_faculty.html      # Admin: Faculty roster & load
│   ├── admin_courses.html      # Admin: Course offerings
│   ├── admin_assignments.html  # Admin: Faculty course allocations
│   ├── admin_monitoring.html   # Admin: Department completion tracking
│   ├── 403.html                # Access forbidden error page
│   └── 404.html                # Page not found error page
├── static/
│   ├── css/
│   │   └── style.css           # Custom CSS variables, cards, tables, print styling
│   └── js/
│       ├── app.js              # State manager (localStorage v2), API service & toasts
│       ├── dashboard.js        # Faculty & Admin dashboard renderers
│       ├── courses.js          # Course search & filtering
│       ├── records.js          # Records controller (syllabus, sessions, marks, attendance, feedback)
│       ├── analytics.js        # CO-PO matrix & attainment charts
│       ├── ai_assistant.js     # Handout parser simulation & sample loader
│       ├── course_file.js      # 8-section checklist & dossier preview renderer
│       └── admin.js            # Admin assignment & monitoring tables
└── tests/
    ├── conftest.py             # Root path discovery for pytest
    └── test_routes.py          # 10 automated test cases (all passing)
```

---

## 4. Quick Start & Execution

### Step 1: Install Requirements
```powershell
pip install -r requirements.txt
```

### Step 2: Start the Web Server
```powershell
python app.py
```

### Step 3: Open in Browser
Open `http://127.0.0.1:5000` in your web browser.

---

## 5. Demo Credentials

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Faculty Member** | `faculty@courseflow.demo` | `courseflow123` | Syllabus, sessions, marks, attendance, feedback, outcomes, course files |
| **Administrator** | `admin@courseflow.demo` | `courseflow123` | Department overview, faculty management, course allocations, monitoring |

*Tip: You can also toggle between roles instantly using the **Demo Role Switcher** inside the user profile menu in the top-right corner.*

---

## 6. Running Automated Tests

Run the full automated test suite using `pytest`:
```powershell
pytest -v
```

All 10 test cases verify:
- Login page rendering and credential validation.
- Successful authentication for both Faculty and Administrator.
- User logout and session invalidation.
- Successful 200 OK rendering across all 15 faculty pages.
- Role-based authorization guardrails (faculty blocked from admin pages with 403).
- Administrative access to all department management pages.
- Backend REST API endpoints (`/api/courses`, `/api/handouts/summarize`, etc.).
- Instant role switching API endpoint.
- Custom 404 error handler for invalid paths.

---

## 7. Viva & Lab Defense Talking Points

When presenting this project during a software engineering evaluation:

1. **Architecture (MVC)**:
   - *Model*: Structured dictionary data in `app.py` mirrored by the reactive `localStorage` store in `static/js/app.js`.
   - *View*: Reusable Jinja templates inheriting from `base.html` with Bootstrap 5 and clean CSS tokens.
   - *Controller*: Flask route handlers coupled with modular vanilla JavaScript controllers.

2. **Decoupled Client Store**:
   - The application uses `CourseFlow.apiService` in `app.js`. If a backend database is connected in the future, only the service methods need to fetch from SQL endpoints—no template rewriting is required.
   - Every button and form performs a tangible action (adds a unit, logs marks, marks attendance, submits feedback, updates checklist).

3. **Explainable Mathematics**:
   - Attendance percentage: `(Present Sessions / Total Sessions) * 100`.
   - Assessment marks percentage: `(Marks / Max Marks) * 100`.
   - Course file completeness: `(Completed Sections / 8) * 100`.
   - Outcome mapping: Simple 0 to 3 scale (Unmapped, Low, Medium, High).

4. **Honest AI Simulation**:
   - The AI assistant clearly states it is in demonstration simulation mode with reproducible test output, highlighting the importance of human-in-the-loop faculty verification before records are saved.

---

## 8. License & Academic Context
Developed for academic assessment in **Software Engineering (CS301)**. All student records, roll numbers, and course data are synthetic demonstration data.
