"""
CourseFlow Comprehensive Database Seeder
Seeds authoritative BML Munjal University and CSE3005 Software Engineering data.
Idempotent and safe: run with --reset to clear and re-populate.
"""

import sys
import os
from flask import Flask
from config import Config
from database import db, init_db
from models import (
    User, Role, Course, FacultyAssignment, CourseFileSection, CourseDocument,
    UniversityInfo, SchoolInfo, GraduateAttribute, PEO,
    ProgramOutcome, ProgramSpecificOutcome, CourseOutcome, CO_PO_Mapping,
    SyllabusModule, SyllabusUnit, SessionPlan, TimetableEntry,
    Student, StudentEnrolment, Assessment, AssessmentComponent,
    StudentMark, AttendanceRecord, StudentFeedback, Intervention,
    COAttainmentRecord, ProjectRequirement, ArchitectureDiagram,
    TestCase, ProjectMilestone, ProjectTask, RiskItem, PertEstimation, AuditLog
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    return app

def seed_database(reset=False, app=None):
    if app is None:
        app = create_app()
    with app.app_context():
        if reset:
            print("Resetting database tables...")
            db.drop_all()
            db.create_all()

        # Check if already seeded
        if User.query.filter_by(email='admin@courseflow.demo').first():
            print("Database already contains seed data. Run with --reset to re-seed.")
            return

        print("1. Seeding Roles & Users...")
        admin_role = Role(name='admin', description='Department / Academic Administrator')
        faculty_role = Role(name='faculty', description='Course Instructor / Coordinator')
        student_role = Role(name='student', description='Enrolled Student')
        db.session.add_all([admin_role, faculty_role, student_role])
        db.session.flush()

        # Users
        admin_user = User(
            email='admin@courseflow.demo',
            name='Dr. Shilpa Mahajan',
            role='admin',
            department='Dept of CSE',
            cabin_office='Cabin No. 7, 4th Floor, E2',
            avatar='SM',
            role_id=admin_role.id
        )
        admin_user.set_password('courseflow123')

        faculty_user = User(
            email='faculty@courseflow.demo',
            name='Dr. Shilpa Mahajan',
            role='faculty',
            department='Dept of CSE',
            cabin_office='Cabin No. 7, 4th Floor, E2',
            avatar='SM',
            role_id=faculty_role.id
        )
        faculty_user.set_password('courseflow123')

        faculty2 = User(
            email='nishtha.phutela@bmu.edu.in',
            name='Dr. Nishtha Phutela',
            role='faculty',
            department='Dept of CSE',
            cabin_office='Cabin No. 63, 4th Floor, E2',
            avatar='NP',
            role_id=faculty_role.id
        )
        faculty2.set_password('courseflow123')

        faculty3 = User(
            email='harsh.taneja@bmu.edu.in',
            name='Dr. Harsh Taneja',
            role='faculty',
            department='Dept of CSE',
            cabin_office='Cabin No. 21, 4th Floor, E2',
            avatar='HT',
            role_id=faculty_role.id
        )
        faculty3.set_password('courseflow123')

        faculty4 = User(
            email='sukhandeep.kaur@bmu.edu.in',
            name='Dr. Sukhandeep Kaur',
            role='faculty',
            department='Dept of CSE',
            cabin_office='Cabin No. 2, 4th Floor, E2',
            avatar='SK',
            role_id=faculty_role.id
        )
        faculty4.set_password('courseflow123')

        db.session.add_all([admin_user, faculty_user, faculty2, faculty3, faculty4])
        db.session.flush()

        print("2. Seeding University & School Information...")
        univ_info = UniversityInfo(
            name='BML Munjal University',
            vision=(
                "BML Munjal University seeks to nurture ethical leaders who are skilled, "
                "knowledgeable and have the life skills required for leading their organizations to success. "
                "The university shall seek the advancement and dissemination of practically oriented knowledge "
                "benchmarked with the best global standards."
            ),
            mission=(
                "BML Munjal University aims to be a leading university for the quality and impact of its teaching, "
                "research, and linkages with major stakeholders. The focus of the university is to find creative "
                "solutions to problems through application of knowledge. The university aims to create a talented "
                "community of students and faculty who excel in teaching, learning and research, in a creative and "
                "stimulating environment. The university will collaborate with other institutions for development "
                "of science, technology, and arts in the global context."
            )
        )
        school_info = SchoolInfo(
            name='School of Engineering & Technology',
            vision=(
                "To be amongst the leading engineering schools of the country recognized globally for excellence "
                "in teaching and research with focus on experiential learning, innovation, and entrepreneurship."
            ),
            mission=(
                "1. Providing high-quality learning experience to our students, preparing them to be global leaders, "
                "and contributing to the development of society through research, innovation, and entrepreneurship.\n"
                "2. Creating an inclusive and diverse learning environment that fosters creativity, critical thinking, and ethical values.\n"
                "3. Collaborating with industry, government, and other institutions to address complex societal challenges and promote sustainable development."
            )
        )
        db.session.add_all([univ_info, school_info])

        print("3. Seeding Graduate Attributes, PEOs, POs, PSOs...")
        gas = [
            GraduateAttribute(code='GA1', title='Discipline Knowledge', description='Acquire and apply practical understanding of discipline knowledge.'),
            GraduateAttribute(code='GA2', title='Ethics & Excellence', description='Demonstrate a sense of ethics and display excellence in both personal and professional life.'),
            GraduateAttribute(code='GA3', title='Problem Solving & Inquiry', description='Exhibit problem solving, critical thinking skills and investigative capability to address real world problems.'),
            GraduateAttribute(code='GA4', title='Leadership & Teamwork', description='Manifest leadership qualities and work effectively in teams across globally diverse environments.'),
            GraduateAttribute(code='GA5', title='Lifelong Learning', description='Be a lifelong learner with an entrepreneurial mindset to innovate in the constantly changing global scenario.'),
            GraduateAttribute(code='GA6', title='Societal Impact', description='Possess a strong sense of inquiry and design innovative solutions for positive societal impact.'),
            GraduateAttribute(code='GA7', title='Effective Communication', description='Be effective communicators and possess an empathetic outlook.')
        ]
        db.session.add_all(gas)

        peos = [
            PEO(code='PEO 1', description='Identify real-life problems and develop creative and innovative hardware/software-based solutions.'),
            PEO(code='PEO 2', description='Achieve professional development through self-learning to adapt to the technological changes in the ever-changing field of computing.'),
            PEO(code='PEO 3', description='Engage in life-long learning of computer engineering technologies, critical thinking and continuous ingenuity and apply them in real-life applications.'),
            PEO(code='PEO 4', description='Accomplish leadership roles by imbibing ethics and professionalism with emphasis on sustainable development of the society.')
        ]
        db.session.add_all(peos)

        pos_data = [
            ('PO1', 'Engineering Knowledge', 'Apply knowledge of mathematics, science, engineering fundamentals, along with Electronics & Computer engineering to the solution of complex engineering problems.'),
            ('PO2', 'Problem Analysis', 'Identify, formulate, review research literature, and analyse complex engineering problems reaching substantiated conclusions using domain knowledge.'),
            ('PO3', 'Design/Development of Solutions', 'Design solutions for complex engineering problems and design system components or processes that meet specified needs with appropriate consideration for public health & safety, cultural, societal, and environmental considerations.'),
            ('PO4', 'Conduct Investigations', 'Use research-based knowledge and research methods including design of experiments, analysis and interpretation of data, and synthesis of information to provide valid conclusions.'),
            ('PO5', 'Modern Tool Usage', 'Select and apply appropriate techniques, resources, and modern engineering tools to various engineering activities with an understanding of limitations.'),
            ('PO6', 'The Engineer and Society', 'Apply reasoning informed by contextual knowledge to assess societal, health, safety, legal and cultural issues and consequent responsibilities.'),
            ('PO7', 'Environment and Sustainability', 'Understand the impact of professional engineering solutions in societal and environmental contexts, and demonstrate knowledge of and need for sustainable development.'),
            ('PO8', 'Ethics', 'Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.'),
            ('PO9', 'Individual and Team Work', 'Function effectively as an individual, and as a member or leader in diverse teams, and in multidisciplinary settings.'),
            ('PO10', 'Communication', 'Communicate effectively on complex engineering activities with the engineering community and with society at large, including report writing and effective presentations.'),
            ('PO11', 'Project Management and Finance', 'Demonstrate knowledge and understanding of engineering and management principles and apply these to manage projects in multidisciplinary environments.'),
            ('PO12', 'Life-long Learning', 'Recognize the need for and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.')
        ]
        for pcode, ptitle, pdesc in pos_data:
            db.session.add(ProgramOutcome(code=pcode, title=ptitle, description=pdesc))

        psos_data = [
            ('PSO1', 'Data Science & Analytics', 'Identify applicable tools and techniques related to data science practice such as data collection, cleaning, analysis, modelling, evaluation, and result interpretation.'),
            ('PSO2', 'Artificial Intelligence & Intelligent Systems', 'Develop intelligent systems for various real-life domains like healthcare, transportation, finance etc. using Artificial Intelligence methodologies.'),
            ('PSO3', 'Cybersecurity Fundamentals', 'Understand foundational concepts and techniques to protect computing systems against constantly evolving cybersecurity threats.'),
            ('PSO4', 'Security System Design', 'Design effective security systems to mitigate risks, threats, and vulnerabilities for protecting organizations against cyber threats.')
        ]
        for scode, stitle, sdesc in psos_data:
            db.session.add(ProgramSpecificOutcome(code=scode, title=stitle, description=sdesc))

        db.session.flush()

        print("4. Seeding CSE3005 Software Engineering Course...")
        se_course = Course(
            id='CSE3005',
            code='CSE3005',
            title='Software Engineering',
            credits=3,
            lecture_hours=2,
            tutorial_hours=0,
            practical_hours=2,
            semester='Semester 4',
            batch='Batch 2024',
            academic_year='2026-27',
            semester_duration='27th July 2025 to 28th Nov 2026',
            department='Computer Science & Engineering',
            school='School of Engineering & Technology',
            university='BML Munjal University',
            aim='The students are expected to learn and understand Software Engineering concepts and techniques that are relevant to the design and development of software systems.',
            overview=(
                "This course introduces software development principles and the lifecycle of software development. "
                "The course explores in detail software development process models, software management principles and challenges, "
                "software requirements analysis and design methodologies, guidelines, tools, and techniques. In addition, "
                "software quality and software maintenance practices will be discussed with hands-on lab exercises and AI-assisted SE."
            ),
            description='Core Software Engineering course covering SDLC, Agile, SRS, MoSCoW, UML/DFD, Verification/Validation, SPM (CPM/PERT), SQA, and AI-assisted SE.',
            status='In Progress',
            coordinator_id=faculty_user.id
        )
        
        # Additional Department Courses for Complete University Offering Catalog
        c_cs301 = Course(id='CS301', code='CS301', title='Software Engineering (Curriculum 2024)', credits=3, semester='Semester 4', batch='Batch 2024', academic_year='2026-27', department='Computer Science & Engineering', status='In Progress', coordinator_id=faculty_user.id)
        c_dbms = Course(id='CS302', code='CS302', title='Database Management Systems', credits=4, semester='Semester 4', batch='Batch 2024', academic_year='2026-27', department='Computer Science & Engineering', status='Completed', coordinator_id=faculty2.id)
        c_daa = Course(id='CS303', code='CS303', title='Design & Analysis of Algorithms', credits=4, semester='Semester 4', batch='Batch 2024', academic_year='2026-27', department='Computer Science & Engineering', status='In Progress', coordinator_id=faculty3.id)
        c_cloud = Course(id='CS401', code='CS401', title='Cloud Computing & DevOps', credits=3, semester='Semester 6', batch='Batch 2023', academic_year='2026-27', department='Computer Science & Engineering', status='In Progress', coordinator_id=faculty4.id)
        c_java = Course(id='CS202', code='CS202', title='Object-Oriented Programming (Java)', credits=4, semester='Semester 3', batch='Batch 2025', academic_year='2026-27', department='Computer Science & Engineering', status='Completed', coordinator_id=faculty_user.id)
        
        db.session.add_all([se_course, c_cs301, c_dbms, c_daa, c_cloud, c_java])
        db.session.flush()

        # Faculty Assignments
        fa1 = FacultyAssignment(course_id='CSE3005', faculty_id=faculty_user.id, role_in_course='Course Coordinator & Theory Instructor')
        fa2 = FacultyAssignment(course_id='CSE3005', faculty_id=faculty2.id, role_in_course='Co-Instructor')
        fa3 = FacultyAssignment(course_id='CSE3005', faculty_id=faculty3.id, role_in_course='Lab Instructor')
        fa4 = FacultyAssignment(course_id='CSE3005', faculty_id=faculty4.id, role_in_course='Lab Instructor')
        db.session.add_all([fa1, fa2, fa3, fa4])

        print("5. Seeding All 25 Course File Sections...")
        sections_spec = [
            (1, "Course Details", "Course-Code, Course Title, Semester, Credits, Contact Hours, Batch, and Academic Year.", "Completed"),
            (2, "Vision, Mission of the University", "BML Munjal University institutional Vision and Mission statement.", "Completed"),
            (3, "Graduate Attributes of the BMU Students", "Seven foundational graduate attributes for BML Munjal University graduates.", "Completed"),
            (4, "Vision, Mission of the School", "School of Engineering & Technology Vision and Mission.", "Completed"),
            (5, "PEOs and POs & PSOs of the Program", "Program Educational Objectives, 12 Program Outcomes, and 4 Program Specific Outcomes for B.Tech CSE.", "Completed"),
            (6, "Course Description and Objectives", "Comprehensive course description, pedagogical context, aim, and learning objectives.", "Completed"),
            (7, "Course Outcomes and CO-PO Mapping", "CO1, CO2, CO3 formulations, Bloom taxonomy mapping, and 12x4 correlation matrix.", "Completed"),
            (8, "Course Syllabus", "7 Syllabus modules, theory/lab hour allocations, textbook references (Sommerville, Pressman), and learning resources.", "Completed"),
            (9, "Detailed Session-wise Plan", "48 session plans (31 Theory + 17 Lab) with mapped COs and pedagogical strategies.", "Completed"),
            (10, "Weekly Timetable", "Weekly class and laboratory schedule with assigned classrooms and faculty.", "Completed"),
            (11, "Registered Students List", "Authorized nominal roll of 58 registered students for Batch 2024 Semester 4.", "Completed"),
            (12, "Details of Internal Assessments", "Assessment pattern: Lab Assessment (40%), Quiz (20%), End Semester Exam (40%).", "Completed"),
            (13, "Mid-Semester Question Papers with Sample Solutions", "Mid-term question papers, marking scheme, and model solutions.", "Completed"),
            (14, "Sample Evaluated Internal Submissions & Identification of Weak Students", "Evaluated answer sheets and identification of students scoring <40%.", "In Progress"),
            (15, "Mid-Term Feedback and Interventions", "Reflections from mid-semester student feedback and pedagogical adjustments.", "Completed"),
            (16, "Interventions for Slow Performers and Advanced Learners", "Remedial lab sessions, retests, and advanced AI-assisted coding challenges.", "Completed"),
            (17, "End-Semester Question Papers with Sample Solutions", "Comprehensive end-term exam question paper and rubric-based sample solutions.", "Completed"),
            (18, "Detail of Marks in all Components", "Consolidated ledger of marks across Lab evaluations, Quiz, and End-Semester exam.", "Completed"),
            (19, "Attendance Report", "Cumulative student attendance report with identification of students below 75% threshold.", "Completed"),
            (20, "Final Record of Results and Grades", "Relative grading distribution, final scores, and grade allocation summary.", "Completed"),
            (21, "Direct Feedback on Course Outcomes", "Course Exit Survey evaluating perceived attainment for CO1, CO2, and CO3.", "Completed"),
            (22, "CO Attainment Measurement Analysis", "Direct (80%) and Indirect (20%) attainment computation and benchmark validation.", "Completed"),
            (23, "Class Committee Feedback and Corrective Actions", "Class committee meeting minutes, student concerns, and faculty actions.", "In Progress"),
            (24, "Faculty Course Review", "End-of-term reflection on experiential learning, AI tools, and future recommendations.", "In Progress"),
            (25, "Additional Information", "Supplementary materials, MoSCoW SRS specifications, and test execution reports.", "Completed")
        ]
        for s_num, s_title, s_desc, s_status in sections_spec:
            db.session.add(CourseFileSection(
                course_id='CSE3005',
                section_number=s_num,
                title=s_title,
                description=s_desc,
                status=s_status,
                updated_by_id=faculty_user.id
            ))

        print("6. Seeding Course Outcomes & Exact CO-PO Mapping...")
        co1 = CourseOutcome(
            course_id='CSE3005',
            code='CO1',
            description='Understanding of fundamental concepts of software engineering, SDLC models, requirement engineering, and software design.',
            mapped_component='Skill Development',
            target_benchmark=70.0,
            class_average=78.4,
            attainment_level=3,
            associated_activities='Interactive lectures, SDLC case studies, requirement elicitation exercises, UML diagram preparation, hands-on lab sessions.'
        )
        co2 = CourseOutcome(
            course_id='CSE3005',
            code='CO2',
            description='Apply software engineering practices to analyze requirements, design, develop, and test software solutions using appropriate methodologies and tools.',
            mapped_component='Employability',
            target_benchmark=70.0,
            class_average=74.6,
            attainment_level=3,
            associated_activities='Agile sprint planning, SRS preparation, UML design tools, Unit and integration testing using PyTest/Selenium.'
        )
        co3 = CourseOutcome(
            course_id='CSE3005',
            code='CO3',
            description='Analyze software project management, software quality, maintenance, and AI-assisted software engineering practices for developing reliable and ethical software systems.',
            mapped_component='Entrepreneurship and Employability',
            target_benchmark=70.0,
            class_average=72.1,
            attainment_level=3,
            associated_activities='Maintenance case studies, PERT/CPM calculations, AI-assisted coding and code review using Copilot/ChatGPT.'
        )
        db.session.add_all([co1, co2, co3])
        db.session.flush()

        # Official CO-PO Mapping Matrix from PDF:
        # CO1: PO1=2, PO2=3, PO3=3, PO4=1, PO5=3, PO6=2, PO8=1, PO10=1, PSO1=1
        co1_maps = [('PO1', 2), ('PO2', 3), ('PO3', 3), ('PO4', 1), ('PO5', 3), ('PO6', 2), ('PO8', 1), ('PO10', 1), ('PSO1', 1)]
        for target, lvl in co1_maps:
            db.session.add(CO_PO_Mapping(course_id='CSE3005', outcome_id=co1.id, outcome_code='CO1', target_code=target, level=lvl))

        # CO2: PO1=3, PO2=2, PO3=3, PO4=2, PO5=3, PO6=2, PO8=2, PO10=2, PSO2=2
        co2_maps = [('PO1', 3), ('PO2', 2), ('PO3', 3), ('PO4', 2), ('PO5', 3), ('PO6', 2), ('PO8', 2), ('PO10', 2), ('PSO2', 2)]
        for target, lvl in co2_maps:
            db.session.add(CO_PO_Mapping(course_id='CSE3005', outcome_id=co2.id, outcome_code='CO2', target_code=target, level=lvl))

        # CO3: PO1=2, PO4=2, PO9=3, PO10=3, PO11=2
        co3_maps = [('PO1', 2), ('PO4', 2), ('PO9', 3), ('PO10', 3), ('PO11', 2)]
        for target, lvl in co3_maps:
            db.session.add(CO_PO_Mapping(course_id='CSE3005', outcome_id=co3.id, outcome_code='CO3', target_code=target, level=lvl))

        print("7. Seeding Syllabus Modules & 48 Session Plans...")
        modules_data = [
            (1, "Introduction to Software Engineering & SDLC", "Introduction to Software Engineering, software characteristics, software crisis, software engineering activities, key challenges, SDLC overview, Waterfall, Incremental, Spiral, Agile development.", "CO1", 6, 2, 8),
            (2, "Requirement Engineering & Prioritization", "Requirement elicitation techniques, requirement analysis, functional and non-functional requirements, MoSCoW requirement prioritization.", "CO1, CO2", 5, 2, 7),
            (3, "Software Design & Architectural Modeling", "Characteristics of software design, modularity, cohesion and coupling, UML (Use Case, Sequence diagrams), Data Flow Diagrams (Context and Level-0 and 1), design documentation.", "CO1, CO2", 4, 2, 6),
            (4, "Coding Standards, Verification & Testing", "Coding standards and coding guidelines, Software verification and validation, unit, integration, system, regression, performance, and security testing, test automation.", "CO2", 6, 4, 10),
            (5, "Software Project Management & Estimation", "Software project monitoring and control, Cost, Effort and Time estimation, Critical Path, PERT Chart.", "CO3", 4, 4, 8),
            (6, "Software Quality Assurance & Maintenance", "Software Quality control and Quality assurance, Necessity of software maintenance, Types of software maintenance, software reverse engineering.", "CO3", 4, 1, 5),
            (7, "AI-Assisted Software Engineering", "Introduction to AI in Software Engineering, Human-in-the-loop validation: Spotting hallucinations and logical bugs. AI-assisted vulnerability scanning and static analysis, Test-driven development (TDD) paired with AI assistants.", "CO3", 2, 2, 4)
        ]
        for m_num, m_title, m_topics, m_cos, th, lh, ts in modules_data:
            db.session.add(SyllabusModule(
                course_id='CSE3005',
                module_number=m_num,
                title=m_title,
                detailed_topics=m_topics,
                mapped_cos=m_cos,
                theory_hours=th,
                lab_hours=lh,
                total_sessions=ts
            ))

        # Sample Session Plans (48 sessions)
        session_topics = [
            (1, 1, "Theory", "Course Overview, SE Definition, Software Crisis & Characteristics", "CO1", "Lecture"),
            (2, 1, "Theory", "Professional Ethics, Key Challenges in Modern Software Engineering", "CO1", "Case Study"),
            (3, 1, "Theory", "SDLC Fundamentals & Classic Waterfall Model", "CO1", "Lecture"),
            (4, 1, "Theory", "Incremental & Spiral Development Process Models", "CO1", "Lecture"),
            (5, 1, "Theory", "Agile Methodologies, Scrum Framework & Sprint Cycles", "CO1", "Interactive Discussion"),
            (6, 1, "Theory", "Comparison of Process Models for Various Project Scales", "CO1", "Case Analysis"),
            (7, 1, "Lab", "Lab 1: Git Workflow, Branching Strategies & GitHub Classroom Setup", "CO1", "Hands-on Practice"),
            (8, 1, "Lab", "Lab 2: Agile Project Board Setup & User Story Mapping", "CO1", "Sprint Setup"),
            (9, 2, "Theory", "Requirement Engineering Concepts & Elicitation Techniques", "CO1", "Lecture"),
            (10, 2, "Theory", "Functional vs Non-Functional Requirements Specification", "CO1", "Lecture"),
            (11, 2, "Theory", "MoSCoW Prioritization Framework & Requirement Triage", "CO1, CO2", "Workshop"),
            (12, 2, "Theory", "IEEE 830 Standard for Software Requirements Specification (SRS)", "CO2", "Documentation"),
            (13, 2, "Theory", "Requirement Validation & Stakeholder Walkthroughs", "CO2", "Review Session"),
            (14, 2, "Lab", "Lab 3: Authoring Complete SRS for CourseFlow CFMS", "CO2", "Lab Exercise"),
            (15, 2, "Lab", "Lab 4: MoSCoW Categorization & Requirement Backlog Grooming", "CO2", "Lab Exercise"),
            (16, 3, "Theory", "Software Design Principles: Modularity, Abstraction & Information Hiding", "CO1", "Lecture"),
            (17, 3, "Theory", "Cohesion Types & Coupling Minimization Strategies", "CO1", "Technical Lecture"),
            (18, 3, "Theory", "UML Behavioral Modeling: Use Case & Sequence Diagrams", "CO2", "Diagram Modeling"),
            (19, 3, "Theory", "Structured Analysis: Context, Level 0 & Level 1 Data Flow Diagrams (DFD)", "CO2", "Diagram Modeling"),
            (20, 3, "Lab", "Lab 5: UML Modeling with Mermaid/StarUML (Use Case & Sequence)", "CO2", "Design Lab"),
            (21, 3, "Lab", "Lab 6: DFD Construction and Architecture Document Generation", "CO2", "Design Lab"),
            (22, 4, "Theory", "Coding Standards, PEP 8, Clean Code Principles & Code Reviews", "CO2", "Lecture"),
            (23, 4, "Theory", "Verification vs Validation, Testing Principles & Bug Lifecycle", "CO2", "Lecture"),
            (24, 4, "Theory", "Unit Testing & Test Driven Development (TDD) Fundamentals", "CO2", "Demonstration"),
            (25, 4, "Theory", "Integration Testing Strategies: Top-Down vs Bottom-Up", "CO2", "Lecture"),
            (26, 4, "Theory", "System & Security Testing, Vulnerability Scanning (OWASP)", "CO2", "Security Workshop"),
            (27, 4, "Theory", "Regression Testing & CI/CD Automated Test Pipelines", "CO2", "DevOps Lecture"),
            (28, 4, "Lab", "Lab 7: PyTest Automated Unit Testing Suite Implementation", "CO2", "Coding Lab"),
            (29, 4, "Lab", "Lab 8: Integration Testing & REST API Endpoint Validation", "CO2", "Coding Lab"),
            (30, 4, "Lab", "Lab 9: Security Vulnerability Scanning & Input Sanitization", "CO2", "Security Lab"),
            (31, 4, "Lab", "Lab 10: Regression Test Automation with GitHub Actions", "CO2", "DevOps Lab"),
            (32, 5, "Theory", "Software Project Management: Planning, Monitoring & Controlling", "CO3", "Lecture"),
            (33, 5, "Theory", "Effort & Cost Estimation: Function Point Analysis & COCOMO", "CO3", "Problem Solving"),
            (34, 5, "Theory", "Activity Networks & Critical Path Method (CPM)", "CO3", "Calculation Workshop"),
            (35, 5, "Theory", "Project Evaluation and Review Technique (PERT): 3-Point Estimation", "CO3", "Calculation Workshop"),
            (36, 5, "Lab", "Lab 11: CPM Network Diagram Construction & Slack Time Analysis", "CO3", "SPM Lab"),
            (37, 5, "Lab", "Lab 12: PERT Expected Time & Project Variance Calculations", "CO3", "SPM Lab"),
            (38, 5, "Lab", "Lab 13: Gantt Chart Scheduling & Task Dependency Mapping", "CO3", "Tools Lab"),
            (39, 5, "Lab", "Lab 14: Risk Register Formulation & Mitigation Planning", "CO3", "Risk Lab"),
            (40, 6, "Theory", "Software Quality Assurance (SQA) vs Quality Control (QC)", "CO3", "Lecture"),
            (41, 6, "Theory", "ISO 9001, CMMI Capability Maturity Model & Quality Metrics", "CO3", "Standards Lecture"),
            (42, 6, "Theory", "Software Maintenance: Corrective, Adaptive, Perfective & Preventive", "CO3", "Lecture"),
            (43, 6, "Theory", "Legacy Code & Reverse Engineering Methodologies", "CO3", "Technical Lecture"),
            (44, 6, "Lab", "Lab 15: Reverse Engineering & Code Smells Refactoring", "CO3", "Refactoring Lab"),
            (45, 7, "Theory", "AI in Software Engineering: LLMs, Coding Assistants & Architecture", "CO3", "Lecture"),
            (46, 7, "Theory", "Human-in-the-Loop Validation: Detecting Hallucinations & Logic Flaws", "CO3", "Discussion"),
            (47, 7, "Lab", "Lab 16: AI-Assisted Vulnerability Scanning & Static Analysis", "CO3", "AI Lab"),
            (48, 7, "Lab", "Lab 17: AI-Assisted TDD & Code Review with Gemini API", "CO3", "Final Project Review")
        ]
        for s_idx, m_idx, s_type, topic, m_co, meth in session_topics:
            db.session.add(SessionPlan(
                course_id='CSE3005',
                session_number=s_idx,
                module_number=m_idx,
                session_type=s_type,
                topic=topic,
                mapped_co=m_co,
                teaching_method=meth,
                status='Completed' if s_idx <= 40 else 'Scheduled'
            ))

        # Timetable
        tt1 = TimetableEntry(course_id='CSE3005', day_of_week='Tuesday', start_time='09:00', end_time='10:50', session_type='Theory', room_location='E2-401', faculty_name='Dr. Shilpa Mahajan')
        tt2 = TimetableEntry(course_id='CSE3005', day_of_week='Thursday', start_time='14:00', end_time='15:50', session_type='Lab', room_location='Lab E2-310', faculty_name='Dr. Harsh Taneja')
        db.session.add_all([tt1, tt2])

        print("8. Seeding Assessments (40% Lab, 20% Quiz, 40% End Sem)...")
        ass_lab = Assessment(course_id='CSE3005', name='Lab Assessment', assessment_type='Internal CIE', weightage_percent=40.0, max_marks=100.0, evaluation_schedule='Oct W3/W4, Nov W1, Nov W4', mapped_cos='CO1, CO2, CO3', rubrics='Code cleanliness, test pass rate, live viva defense')
        ass_quiz = Assessment(course_id='CSE3005', name='Quiz', assessment_type='Internal CIE', weightage_percent=20.0, max_marks=50.0, evaluation_schedule='Mid Term Exam Week (Offline)', mapped_cos='CO1', rubrics='Multiple choice & conceptual questions')
        ass_see = Assessment(course_id='CSE3005', name='End Semester Examination', assessment_type='External SEE', weightage_percent=40.0, max_marks=100.0, evaluation_schedule='University Scheduled End Term', mapped_cos='CO1, CO2, CO3', rubrics='Comprehensive theoretical & analytical examination')
        db.session.add_all([ass_lab, ass_quiz, ass_see])
        db.session.flush()

        print("9. Seeding 58 Demo Students with Marks & Attendance (Adhering to Phase 12 Data Integrity)...")
        first_names = ["Aarav", "Aditi", "Aditya", "Akash", "Ananya", "Aniket", "Anushka", "Arjun", "Armaan", "Aryan",
                       "Ayush", "Bhavya", "Chaitanya", "Devansh", "Diya", "Dhruv", "Gauri", "Harsh", "Ishaan", "Jhanvi",
                       "Kabir", "Kavya", "Khushi", "Krish", "Madhav", "Manish", "Meera", "Mihir", "Nandini", "Navya",
                       "Nikhil", "Parth", "Pranav", "Prisha", "Rahul", "Rhea", "Rishi", "Riya", "Rohan", "Sahil",
                       "Samar", "Sanya", "Shaurya", "Shiv", "Shreya", "Siddharth", "Simran", "Sneha", "Sparsh", "Tanvi",
                       "Tarun", "Uday", "Utkarsh", "Vaishnavi", "Varun", "Vedant", "Vidhi", "Yash"]
        
        last_names = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Mehta", "Jain", "Chopra", "Malhotra", "Kapoor"]

        students = []
        for i in range(58):
            roll = f"2401010{i+1:02d}"
            name = f"{first_names[i]} {last_names[i % len(last_names)]}"
            email = f"{first_names[i].lower()}.{last_names[i % len(last_names)].lower()}@bmu.edu.in"
            stud = Student(roll_no=roll, name=name, email=email, batch='Batch 2024', semester='Semester 4', is_demo_data=True)
            db.session.add(stud)
            students.append(stud)
        db.session.flush()

        # Enrolments, Attendance & Marks
        for idx, stud in enumerate(students):
            # Enrolment
            db.session.add(StudentEnrolment(student_id=stud.id, course_id='CSE3005'))
            
            # Attendance: Make 6 students below 75% for intervention showcase (e.g. index 7, 18, 25, 34, 42, 53)
            if idx in [7, 18, 25, 34, 42, 53]:
                attended = 32  # 32 / 48 = 66.7%
            elif idx in [12, 30]:
                attended = 37  # 37 / 48 = 77.1% (Warning)
            else:
                attended = 40 + (idx % 8)  # 83% - 100%
            
            att_rec = AttendanceRecord(
                course_id='CSE3005',
                student_id=stud.id,
                total_classes=48,
                attended_classes=attended
            )
            att_rec.update_status()
            db.session.add(att_rec)

            # Marks: Lab Assessment (out of 100)
            if idx in [7, 25]:  # Weak students (<40)
                lab_score = 36.0
                quiz_score = 16.0  # out of 50
                see_score = 38.0
                grade = 'F'
                is_weak = True
            elif idx in [18, 34]:
                lab_score = 52.0
                quiz_score = 26.0
                see_score = 54.0
                grade = 'D'
                is_weak = False
            else:
                lab_score = 65.0 + (idx % 30)
                quiz_score = 35.0 + (idx % 14)
                see_score = 68.0 + (idx % 28)
                grade = 'A' if lab_score > 85 else ('B+' if lab_score > 75 else 'B')
                is_weak = False

            db.session.add(StudentMark(course_id='CSE3005', student_id=stud.id, assessment_id=ass_lab.id, marks_obtained=min(lab_score, 98.0), max_marks=100.0, grade=grade, is_weak_student=is_weak))
            db.session.add(StudentMark(course_id='CSE3005', student_id=stud.id, assessment_id=ass_quiz.id, marks_obtained=min(quiz_score, 49.0), max_marks=50.0, grade=grade, is_weak_student=is_weak))
            db.session.add(StudentMark(course_id='CSE3005', student_id=stud.id, assessment_id=ass_see.id, marks_obtained=min(see_score, 96.0), max_marks=100.0, grade=grade, is_weak_student=is_weak))

        print("10. Seeding Interventions & Feedback...")
        interv1 = Intervention(
            course_id='CSE3005',
            category='Slow Performer',
            reason='Scored below 40% in Lab Assessment 1 and Quiz 1',
            action_taken='Conducted 2 remedial lab sessions on PyTest test automation and provided simplified step-by-step UML exercises.',
            outcome_observed='Retest conducted; score improved from 36% to 62%.',
            status='Resolved'
        )
        interv2 = Intervention(
            course_id='CSE3005',
            category='Slow Performer',
            reason='Attendance critical at 66.7% (<75% threshold)',
            action_taken='Parental notification issued and mandatory supplementary tutorial assigned on Friday mornings.',
            outcome_observed='Attendance stabilized above 75% for remaining modules.',
            status='In Progress'
        )
        interv3 = Intervention(
            course_id='CSE3005',
            category='Advanced Learner',
            reason='Scored 95%+ in lab assignments with exceptional software design architecture',
            action_taken='Assigned capstone research challenge: Implement AI-assisted security scanner using Gemini API and static AST analysis.',
            outcome_observed='Delivered automated vulnerability scanner demo to class.',
            status='Resolved'
        )
        db.session.add_all([interv1, interv2, interv3])

        fb1 = StudentFeedback(
            course_id='CSE3005',
            feedback_type='Mid-Term',
            rating_co1=4.4,
            rating_co2=4.2,
            rating_co3=4.1,
            overall_rating=4.25,
            comments='Hands-on lab exercises and Agile sprint demos significantly improved understanding. Requested extra practice on PERT/CPM calculations.',
            corrective_actions='Added 1 dedicated problem-solving tutorial session for Critical Path and PERT variance before end-term exams.'
        )
        fb2 = StudentFeedback(
            course_id='CSE3005',
            feedback_type='Exit Survey',
            rating_co1=4.6,
            rating_co2=4.4,
            rating_co3=4.3,
            overall_rating=4.45,
            comments='Practical exposure to CourseFlow CFMS architecture made Software Engineering theory tangible and memorable.',
            corrective_actions='Incorporate industry guest session on cloud CI/CD pipelines in future iterations.'
        )
        db.session.add_all([fb1, fb2])

        # CO Attainment Records
        db.session.add(COAttainmentRecord(course_id='CSE3005', outcome_code='CO1', direct_attainment=79.2, indirect_attainment=85.0, overall_attainment=80.4, students_evaluated=58, students_attained=51, attainment_percentage=87.9, attainment_level=3, target_benchmark=70.0))
        db.session.add(COAttainmentRecord(course_id='CSE3005', outcome_code='CO2', direct_attainment=74.8, indirect_attainment=82.5, overall_attainment=76.3, students_evaluated=58, students_attained=48, attainment_percentage=82.8, attainment_level=3, target_benchmark=70.0))
        db.session.add(COAttainmentRecord(course_id='CSE3005', outcome_code='CO3', direct_attainment=72.5, indirect_attainment=81.0, overall_attainment=74.2, students_evaluated=58, students_attained=47, attainment_percentage=81.0, attainment_level=3, target_benchmark=70.0))

        print("11. Seeding Software Engineering Lifecycle: SRS, MoSCoW, Diagrams, Tests & SPM...")
        # Requirements & MoSCoW
        reqs = [
            ProjectRequirement(req_id='FR-01', title='Role-Based Authentication & Session Access', description='The system must enforce secure login with password hashing and restrict administrator vs faculty views.', category='Functional', moscow='Must Have', status='Implemented', stakeholder='Faculty & Admin', acceptance_criteria='Invalid passwords rejected; role routes restricted.'),
            ProjectRequirement(req_id='FR-02', title='25-Section Course File Status Tracking', description='The system must track status (Not Started, In Progress, Completed, Needs Review) across all 25 official university sections.', category='Functional', moscow='Must Have', status='Implemented', stakeholder='Course Coordinator', acceptance_criteria='All 25 sections displayed with live completion percentage.'),
            ProjectRequirement(req_id='FR-03', title='Outcome-Based Attainment Ledger', description='The system must compute and display CO attainment against target benchmarks with difference indicators.', category='Functional', moscow='Must Have', status='Implemented', stakeholder='NBA Accreditation Coordinator', acceptance_criteria='Attainment calculated from direct CIE/SEE and indirect exit surveys.'),
            ProjectRequirement(req_id='FR-04', title='Attendance Shortage Identification (<75%)', description='The system must highlight students whose cumulative attendance falls below the mandatory 75% threshold.', category='Functional', moscow='Must Have', status='Implemented', stakeholder='Course Faculty', acceptance_criteria='Students below 75% flagged with critical danger badge.'),
            ProjectRequirement(req_id='FR-05', title='AI Course Handout Summarizer (Gemini API)', description='The system must extract structured summaries, topics, and suggested COs from uploaded PDF/DOCX course handouts.', category='Functional', moscow='Should Have', status='Implemented', stakeholder='Course Faculty', acceptance_criteria='Valid JSON returned with summary, topics, and CO suggestions.'),
            ProjectRequirement(req_id='FR-06', title='Course File Handout Document Preview & Print', description='The system must render a consolidated HTML course handout matching university formatting for PDF export.', category='Functional', moscow='Should Have', status='Implemented', stakeholder='Faculty & Academic Auditor', acceptance_criteria='Formatted multi-section document rendered with print stylesheets.'),
            ProjectRequirement(req_id='FR-07', title='Intervention Tracking for Slow & Advanced Learners', description='The system must document remediation initiatives and advanced study tasks with outcome observations.', category='Functional', moscow='Could Have', status='Implemented', stakeholder='Course Faculty', acceptance_criteria='Records categorized as Slow Performer or Advanced Learner.'),
            ProjectRequirement(req_id='FR-08', title='Automated Biometric Hardware Sync', description='Direct hardware integration with physical biometric classroom scanners.', category='Functional', moscow="Won't Have", status='Proposed', stakeholder='Campus IT', acceptance_criteria='Deferred to future release; manual entry & Excel import supported.'),
            ProjectRequirement(req_id='NFR-01', title='Persistent Relational Storage Integrity', description='All records must persist to hosted PostgreSQL (Supabase) with foreign key constraints.', category='Non-Functional', moscow='Must Have', status='Implemented', stakeholder='DevOps / Database Administrator', acceptance_criteria='Data preserved across restarts with zero localStorage reliance for source of truth.'),
            ProjectRequirement(req_id='NFR-02', title='Response Time & Latency Benchmarks', description='Page load response time must not exceed 1.5 seconds for core dashboards under normal loads.', category='Non-Functional', moscow='Should Have', status='Implemented', stakeholder='End Users', acceptance_criteria='Optimized SQLAlchemy queries with lazy loading.'),
            ProjectRequirement(req_id='NFR-03', title='Security & OWASP Compliance', description='Sanitized SQL inputs via ORM parameterization; secure HTTP session cookies; protected credentials.', category='Non-Functional', moscow='Must Have', status='Implemented', stakeholder='Security Auditor', acceptance_criteria='Zero SQL injection vectors; environment variables for API secrets.')
        ]
        db.session.add_all(reqs)

        # Architecture Diagrams (11 diagrams)
        diagrams = [
            ArchitectureDiagram(
                diagram_type='Use Case',
                title='CourseFlow System Use Case Diagram',
                description='Actor boundaries between Faculty and Administrator showcasing syllabus planning, attendance, marks, attainment, and course file compilation.',
                mermaid_code="""graph LR
    Faculty["Faculty User"]
    Admin["System Administrator"]
    
    subgraph CourseFlow ["CourseFlow CFMS"]
        UC1((Login & Auth))
        UC2((Manage 25-Section Course File))
        UC3((Record Attendance & Filter <75%))
        UC4((Enter Assessment Marks))
        UC5((Compute CO-PO Attainment))
        UC6((AI Handout Summarization))
        UC7((Generate Course File PDF))
        UC8((Assign Courses & Faculty))
        UC9((Monitor Department Compliance))
    end
    
    Faculty --> UC1
    Faculty --> UC2
    Faculty --> UC3
    Faculty --> UC4
    Faculty --> UC5
    Faculty --> UC6
    Faculty --> UC7
    
    Admin --> UC1
    Admin --> UC8
    Admin --> UC9
    Admin --> UC2""",
                components_involved='Auth, Course File, Records, Analytics, AI Assistant, Admin'
            ),
            ArchitectureDiagram(
                diagram_type='Class',
                title='Domain Model Class Diagram',
                description='Relational schema structure illustrating Course, CourseFileSection, User, Student, Assessment, StudentMark, AttendanceRecord, and Outcomes.',
                mermaid_code="""classDiagram
    class User {
        +Integer id
        +String email
        +String name
        +String role
        +check_password()
    }
    class Course {
        +String id
        +String code
        +String title
        +Integer credits
        +calculate_completion()
    }
    class CourseFileSection {
        +Integer section_number
        +String title
        +String status
    }
    class Student {
        +String roll_no
        +String name
        +Boolean is_demo_data
    }
    class Assessment {
        +String name
        +Float weightage_percent
    }
    class StudentMark {
        +Float marks_obtained
        +String grade
    }
    class AttendanceRecord {
        +Integer attended_classes
        +Float percentage
        +String status
    }
    class CourseOutcome {
        +String code
        +Float target_benchmark
        +Float class_average
    }
    
    User "1" --> "*" Course : coordinates
    Course "1" --> "25" CourseFileSection : contains
    Course "1" --> "*" Student : enrolls
    Course "1" --> "*" Assessment : defines
    Course "1" --> "3" CourseOutcome : targets
    Student "1" --> "*" StudentMark : obtains
    Assessment "1" --> "*" StudentMark : assesses
    Student "1" --> "1" AttendanceRecord : logs""",
                components_involved='models.user, models.course, models.student, models.curriculum'
            ),
            ArchitectureDiagram(
                diagram_type='Sequence',
                title='Outcome Attainment Computation Sequence Diagram',
                description='Execution flow when faculty triggers recalculation of direct CIE/SEE and indirect survey marks.',
                mermaid_code="""sequenceDiagram
    autonumber
    actor Faculty as Faculty User
    participant Browser as Web Interface
    participant Route as Attainment Controller
    participant Service as Attainment Engine
    participant DB as Hosted PostgreSQL (Supabase)

    Faculty->>Browser: Click 'Calculate Attainment'
    Browser->>Route: POST /api/attainment/calculate
    Route->>Service: compute_course_attainment('CSE3005')
    Service->>DB: Query StudentMarks (CIE & SEE)
    DB-->>Service: Return Marks dataset
    Service->>DB: Query ExitSurvey ratings
    DB-->>Service: Return Feedback records
    Service->>Service: Aggregate Direct (80%) + Indirect (20%)
    Service->>DB: UPDATE co_attainment_records
    DB-->>Service: Commit transaction
    Service-->>Route: Return calculated percentages & levels
    Route-->>Browser: JSON payload with CO attainment status
    Browser-->>Faculty: Render 5-column ledger & Chart.js graph""",
                components_involved='routes.api_routes, services.attainment_service, PostgreSQL'
            ),
            ArchitectureDiagram(
                diagram_type='Context DFD',
                title='Level 0 / Context Data Flow Diagram',
                description='High-level boundary representation of CourseFlow interacting with external entities (Faculty, Administrator, Students, and Gemini AI).',
                mermaid_code="""graph TD
    Faculty[Faculty Member] -->|Course Handouts, Marks, Attendance| CF[CourseFlow CFMS - System Context]
    Admin[Academic Admin] -->|Course Allocations, Role Assignments| CF
    CF -->|Course File PDF, Attainment Reports| Faculty
    CF -->|Department Audit & Compliance Summaries| Admin
    CF -->|Handout Document Bytes| Gemini[Google Gemini 2.5 Flash API]
    Gemini -->|Extracted Summaries & Topics| CF
    CF -->|Persistent Relational Transactions| Supabase[(PostgreSQL / Supabase)]
    Supabase -->|Stored Records & Entities| CF""",
                components_involved='Faculty, Administrator, External Gemini API, Supabase DB'
            ),
            ArchitectureDiagram(
                diagram_type='Level 1 DFD',
                title='Level 1 Functional Data Flow Diagram',
                description='Decomposition of internal CourseFlow sub-processes: Auth (1.0), Course File Mgmt (2.0), Attendance & Marks (3.0), Attainment Engine (4.0), and AI Handout Parser (5.0).',
                mermaid_code="""graph TD
    User([User]) -->|Credentials| P1[1.0 Authenticate & Authorize]
    P1 --> D1[(Users & Roles)]
    
    User -->|Section Content & Attachments| P2[2.0 Course File Management]
    P2 --> D2[(Course File Sections)]
    
    User -->|Marks & Attendance Data| P3[3.0 Records & Assessment Management]
    P3 --> D3[(Marks & Attendance Records)]
    
    D3 --> P4[4.0 OBE Outcome Attainment Engine]
    D2 --> P4
    P4 --> D4[(Attainment & CO-PO Matrices)]
    
    User -->|Handout Document| P5[5.0 AI Handout Summarizer]
    P5 -->|API Call| ExtAI[Gemini 2.5 Flash]
    ExtAI -->|Structured JSON| P5
    P5 --> D2
    
    P4 -->|Report Generation| Output([Audit-Ready Course File])""",
                components_involved='Processes 1.0 - 5.0 and Relational Data Stores'
            ),
            ArchitectureDiagram(
                diagram_type='State Transition',
                title='Course File Section Lifecycle State Machine',
                description='Status transitions for any of the 25 course file sections from initiation through faculty completion and administrative review.',
                mermaid_code="""stateDiagram-v2
    [*] --> NotStarted: Course Initialized
    NotStarted --> InProgress: Faculty adds data / attaches files
    InProgress --> Completed: All mandatory fields satisfied
    Completed --> NeedsReview: Academic audit flags revision
    NeedsReview --> InProgress: Faculty applies corrective actions
    Completed --> Archived: End-of-Semester Signoff
    Archived --> [*]""",
                components_involved='models.course.CourseFileSection.status'
            ),
            ArchitectureDiagram(
                diagram_type='Database ER',
                title='Entity Relationship (ER) Diagram',
                description='Complete normalized entity relational structure connecting all 28 tables in CourseFlow PostgreSQL database.',
                mermaid_code="""erDiagram
    USERS ||--o{ COURSES : coordinates
    USERS ||--o{ FACULTY_ASSIGNMENTS : assigned
    COURSES ||--|{ COURSE_FILE_SECTIONS : contains
    COURSES ||--o{ SYLLABUS_MODULES : organizes
    COURSES ||--o{ COURSE_OUTCOMES : defines
    COURSE_OUTCOMES ||--o{ CO_PO_MAPPINGS : maps_to
    PROGRAM_OUTCOMES ||--o{ CO_PO_MAPPINGS : receives
    COURSES ||--o{ ASSESSMENTS : evaluates
    COURSES ||--o{ STUDENT_ENROLMENTS : enrolls
    STUDENTS ||--o{ STUDENT_ENROLMENTS : joins
    STUDENTS ||--o{ ATTENDANCE_RECORDS : logs
    STUDENTS ||--o{ STUDENT_MARKS : earns
    ASSESSMENTS ||--o{ STUDENT_MARKS : scores
    COURSES ||--o{ INTERVENTIONS : triggers
    COURSES ||--o{ CO_ATTAINMENT_RECORDS : measures""",
                components_involved='All 28 Relational Entities'
            )
        ]
        db.session.add_all(diagrams)

        # Test Cases (QA)
        test_cases = [
            TestCase(test_id='AUTH-TC01', module='Authentication', test_type='Unit', test_scenario='Verify password hashing using werkzeug generate_password_hash', preconditions='User instance created', test_inputs='Password: courseflow123', expected_output='Password hash is not plaintext and check_password returns True', actual_output='Hash validated successfully', test_result='Pass', severity='Critical', tester='Security Engineer'),
            TestCase(test_id='AUTH-TC02', module='Authentication', test_type='System', test_scenario='Reject invalid password during faculty login', preconditions='User exists in database', test_inputs='Email: faculty@courseflow.demo, Password: wrongpassword', expected_output='HTTP 200 with error flash: Invalid password', actual_output='Error message displayed; session not set', test_result='Pass', severity='High', tester='QA Lead'),
            TestCase(test_id='AUTH-TC03', module='Authentication', test_type='Security', test_scenario='Prevent unauthorized access to /admin routes by faculty role', preconditions='Logged in as faculty', test_inputs='GET /admin/faculty', expected_output='HTTP 403 Forbidden with access restriction banner', actual_output='HTTP 403 rendered', test_result='Pass', severity='Critical', tester='Security Auditor'),
            TestCase(test_id='CF-TC01', module='Course File', test_type='System', test_scenario='Verify all 25 sections load with status badges', preconditions='Course CSE3005 seeded', test_inputs='GET /course-file', expected_output='All 25 sections displayed from Section 1 to Section 25', actual_output='25 sections rendered with status pills', test_result='Pass', severity='High', tester='Lead Tester'),
            TestCase(test_id='CF-TC02', module='Course File', test_type='Unit', test_scenario='Calculate overall course file completion percentage', preconditions='21 of 25 sections completed', test_inputs='calculate_completion()', expected_output='Returns 84%', actual_output='Returned 84%', test_result='Pass', severity='Medium', tester='QA Tester'),
            TestCase(test_id='REC-TC01', module='Records', test_type='System', test_scenario='Identify students below 75% attendance threshold', preconditions='Attendance table populated', test_inputs='Filter isShortage == True', expected_output='6 students flagged with Critical danger alert', actual_output='6 students correctly highlighted', test_result='Pass', severity='High', tester='QA Tester'),
            TestCase(test_id='REC-TC02', module='Records', test_type='Unit', test_scenario='Identify weak students scoring below 40% in internal assessments', preconditions='Student marks populated', test_inputs='Filter is_weak_student == True', expected_output='Identifies weak students for Section 14 & 16 interventions', actual_output='2 weak students identified and listed', test_result='Pass', severity='Medium', tester='QA Tester'),
            TestCase(test_id='OBE-TC01', module='Attainment', test_type='System', test_scenario='Calculate direct and indirect CO attainment percentages', preconditions='Marks and survey feedback recorded', test_inputs='Trigger calculation', expected_output='CO1: 80.4%, CO2: 76.3%, CO3: 74.2% (Level 3 Attained)', actual_output='Values match mathematical specifications', test_result='Pass', severity='High', tester='OBE Auditor'),
            TestCase(test_id='AI-TC01', module='Handout Summarizer', test_type='Integration', test_scenario='Reject executable file upload (.exe)', preconditions='Active Gemini API key', test_inputs='Upload malicious.exe', expected_output='HTTP 400 with "Unsupported file type: .exe"', actual_output='HTTP 400 returned with validation message', test_result='Pass', severity='High', tester='Security Tester'),
            TestCase(test_id='AI-TC02', module='Handout Summarizer', test_type='Integration', test_scenario='Extract structured summary and CO suggestions from PDF', preconditions='Valid SE_CSE3005 handout PDF', test_inputs='POST /api/handouts/summarize', expected_output='JSON with summary, topics, and suggested COs', actual_output='Structured JSON returned in 2.8s', test_result='Pass', severity='Medium', tester='AI Engineer')
        ]
        db.session.add_all(test_cases)

        # Software Project Management (SPM)
        m1 = ProjectMilestone(title='Sprint 1: Architecture, Inception & Database Schema', start_date='2026-09-01', due_date='2026-09-20', status='Completed', completion_percent=100)
        m2 = ProjectMilestone(title='Sprint 2: 25-Section Course File & Content Migration', start_date='2026-09-21', due_date='2026-10-15', status='Completed', completion_percent=100)
        m3 = ProjectMilestone(title='Sprint 3: OBE Attainment Engine & Attendance Analytics', start_date='2026-10-16', due_date='2026-11-05', status='Completed', completion_percent=100)
        m4 = ProjectMilestone(title='Sprint 4: AI Summarizer & Academic Report Generator', start_date='2026-11-06', due_date='2026-11-20', status='Completed', completion_percent=100)
        m5 = ProjectMilestone(title='Sprint 5: End-Term Viva Verification & Demonstration', start_date='2026-11-21', due_date='2026-11-28', status='In Progress', completion_percent=90)
        db.session.add_all([m1, m2, m3, m4, m5])
        db.session.flush()

        tasks = [
            ProjectTask(milestone_id=m1.id, title='Normalize 28 relational database entities', assignee='Database Architect', priority='High', status='Done', estimated_hours=12.0, actual_hours=11.5),
            ProjectTask(milestone_id=m1.id, title='Configure Supabase PostgreSQL connection layer', assignee='DevOps Engineer', priority='High', status='Done', estimated_hours=8.0, actual_hours=7.0),
            ProjectTask(milestone_id=m2.id, title='Implement 25-section course file navigation and status tracking', assignee='Frontend Lead', priority='High', status='Done', estimated_hours=16.0, actual_hours=15.0),
            ProjectTask(milestone_id=m2.id, title='Extract and seed CSE3005 official syllabus and 48 sessions', assignee='Full-Stack Dev', priority='Medium', status='Done', estimated_hours=10.0, actual_hours=9.5),
            ProjectTask(milestone_id=m3.id, title='Build direct and indirect CO attainment calculation service', assignee='Backend Dev', priority='High', status='Done', estimated_hours=14.0, actual_hours=13.0),
            ProjectTask(milestone_id=m3.id, title='Implement student attendance shortage warning logic (<75%)', assignee='Full-Stack Dev', priority='Medium', status='Done', estimated_hours=6.0, actual_hours=5.5),
            ProjectTask(milestone_id=m4.id, title='Integrate Google Gemini 2.5 Flash for handout parsing', assignee='AI Engineer', priority='Medium', status='Done', estimated_hours=10.0, actual_hours=9.0),
            ProjectTask(milestone_id=m5.id, title='Author automated pytest test suite and viva demo checklist', assignee='QA & Project Manager', priority='High', status='In Progress', estimated_hours=12.0, actual_hours=10.0)
        ]
        db.session.add_all(tasks)

        # Risks
        risks = [
            RiskItem(risk_id='RSK-01', description='External Supabase connection timeout due to campus proxy restrictions', category='Technical', probability='Medium', impact='High', mitigation_strategy='Implemented graceful local SQLite fallback if DATABASE_URL is unreachable.', status='Mitigated'),
            RiskItem(risk_id='RSK-02', description='Accidental mixing of CSE2724 HCI student dataset into CSE3005 Software Engineering', category='Operational', probability='Low', impact='Critical', mitigation_strategy='Enforced strict Phase 12 validation: isolated HCI sheet and seeded distinct demo records.', status='Mitigated'),
            RiskItem(risk_id='RSK-03', description='Gemini API quota exhaustion during live faculty presentation', category='Technical', probability='Low', impact='Medium', mitigation_strategy='Added structured offline sample fallback response if external API returns HTTP 429.', status='Mitigated')
        ]
        db.session.add_all(risks)

        # PERT Estimations
        perts = [
            PertEstimation(task_name='Database Architecture & Normalization', optimistic_days=2.0, most_likely_days=3.5, pessimistic_days=6.0, is_critical_path=True),
            PertEstimation(task_name='25-Section Course File Implementation', optimistic_days=3.0, most_likely_days=5.0, pessimistic_days=8.0, is_critical_path=True),
            PertEstimation(task_name='OBE Outcome Attainment Calculations', optimistic_days=2.5, most_likely_days=4.0, pessimistic_days=7.0, is_critical_path=True),
            PertEstimation(task_name='AI Handout Summarization & Gemini Integration', optimistic_days=1.5, most_likely_days=3.0, pessimistic_days=5.5, is_critical_path=False),
            PertEstimation(task_name='Automated PyTest Testing & Verification', optimistic_days=2.0, most_likely_days=3.0, pessimistic_days=5.0, is_critical_path=True)
        ]
        for p in perts:
            p.calculate()
            db.session.add(p)

        # Audit Log
        db.session.add(AuditLog(user_id=admin_user.id, action='SEED_DATABASE', module='System', details='Initialized CourseFlow relational database with official BML Munjal University CSE3005 dataset.'))

        db.session.commit()
        print("Database seeded successfully with all official entities, CSE3005 content, and Software Engineering lifecycle modules!")

if __name__ == '__main__':
    reset_flag = '--reset' in sys.argv
    seed_database(reset=reset_flag)
