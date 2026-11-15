# CourseFlow (CFMS) – Known Limitations & Academic Transparency Log

**Project:** CourseFlow – Course File Management System  
**Institution:** BML Munjal University  
**Date:** November 16, 2026  
**Purpose:** Honest, professional disclosure of technical scope boundaries and source data constraints for academic viva defense.

---

## 1. Source Data Constraints & Provenance

### Attendance Registers
- **Constraint:** The official university workbook `CSE2724.xlsx` (Sheet: Clean Maitri Data) contains complete, authentic continuous evaluation marks (Lab, Project, SEE) and final grades for all 391 students, but does **not** include nominal session-by-session attendance logs.
- **Academic Transparency Measure:** The attendance records in CourseFlow (16 sessions, 89.8% average, 10 shortage warnings) are explicitly classified as **SAMPLE / DEMO DATA (SYNTHESIZED)**. Every attendance view, report, and dossier section displays a visible badge to ensure complete academic honesty.
- **System Capability:** The attendance subsystem is fully implemented with session-wise recording, individual overrides, and threshold alerts, ready to ingest real daily logs when provided.

### Course Outcome Exit Surveys (Indirect Attainment)
- **Constraint:** Raw student exit survey feedback forms were not included in `CSE2724.xlsx`.
- **Academic Transparency Measure:** Survey attainment values (85.0% rating across COs) are clearly flagged as **ESTIMATED / SAMPLE DATA** in Section 21 and the attainment ledger.

---

## 2. Infrastructure & Hosting Environment

### Local SQLite vs Cloud PostgreSQL
- **Active Setup:** The application currently runs on a robust, persistent local **SQLite database** (`courseflow.db`), backed up safely to `courseflow_pre_final_implementation.db`.
- **Limitation:** While CourseFlow's SQLAlchemy ORM models are 100% compatible with PostgreSQL and Supabase, live cloud connection strings are subject to institutional network egress and proxy firewalls on student workstations.
- **Viva Defense Rationale:** Demonstrating on local SQLite guarantees zero latency, zero internet-dependency failure during presentation, and 100% data persistence.

### Google Gemini API Quotas
- **Constraint:** The AI Handout Assistant communicates with the Google Gemini API (`gemini-1.5-flash`). Free-tier API keys may encounter rate limits (15 requests per minute) if multiple large documents are uploaded in rapid succession.
- **Graceful Degradation:** CourseFlow implements comprehensive client-side error handling, displaying explanatory toast notifications and offering sample fallback data if an API quota is exhausted.

---

## 3. Browser Print & Export Formatting

### Print CSS & PDF Generation
- **Behavior:** The one-click course dossier preview (`/course-file/preview`) uses standard CSS `@media print` rules for browser PDF export (`window.print()`).
- **Limitation:** Minor pagination breaks may vary slightly between Chromium (Chrome, Edge), Firefox, and Safari depending on individual operating system DPI and margin settings.
- **Recommendation:** Evaluators are recommended to use Google Chrome or Microsoft Edge with "Save as PDF" and "Default Margins" for optimal dossier rendering.
