/**
 * CourseFlow - Course File Management System (CFMS)
 * Master Client Application & Data Adapter Layer (Simplified)
 */

// ==========================================================================
// 1. DEFAULT DEMO DATA STORE
// ==========================================================================
const DEFAULT_STORE = {
  currentUser: {
    name: 'Dr. Sarah Jenkins',
    email: 'faculty@courseflow.demo',
    role: 'faculty', // 'faculty' or 'admin'
    department: 'Computer Science & Engineering',
    avatar: 'SJ'
  },
  courses: [
    {
      id: 'CS301',
      code: 'CS301',
      title: 'Software Engineering',
      semester: 'Semester 5',
      academicYear: '2024-2025',
      faculty: 'Dr. Sarah Jenkins',
      facultyEmail: 'faculty@courseflow.demo',
      studentsCount: 58,
      completion: 88,
      status: 'In Progress',
      credits: 4,
      department: 'Computer Science & Engineering',
      description: 'Comprehensive study of software lifecycle models, requirements engineering, architectural design, agile methodologies, testing techniques, and project management.'
    },
    {
      id: 'CS302',
      code: 'CS302',
      title: 'Database Management Systems',
      semester: 'Semester 5',
      academicYear: '2024-2025',
      faculty: 'Dr. Sarah Jenkins',
      facultyEmail: 'faculty@courseflow.demo',
      studentsCount: 62,
      completion: 100,
      status: 'Completed',
      credits: 4,
      department: 'Computer Science & Engineering',
      description: 'Relational data models, normalization, SQL, indexing, transaction processing, concurrency control, and NoSQL architecture.'
    },
    {
      id: 'CS303',
      code: 'CS303',
      title: 'Design & Analysis of Algorithms',
      semester: 'Semester 5',
      academicYear: '2024-2025',
      faculty: 'Prof. Rajesh Sharma',
      facultyEmail: 'admin@courseflow.demo',
      studentsCount: 55,
      completion: 75,
      status: 'In Progress',
      credits: 4,
      department: 'Computer Science & Engineering',
      description: 'Asymptotic notation, divide-and-conquer, greedy techniques, dynamic programming, graph algorithms, and NP-completeness.'
    },
    {
      id: 'CS401',
      code: 'CS401',
      title: 'Cloud Computing & DevOps',
      semester: 'Semester 7',
      academicYear: '2024-2025',
      faculty: 'Dr. Sarah Jenkins',
      facultyEmail: 'faculty@courseflow.demo',
      studentsCount: 48,
      completion: 88,
      status: 'In Progress',
      credits: 3,
      department: 'Computer Science & Engineering',
      description: 'Virtualization, microservices, containerization with Docker & Kubernetes, CI/CD pipelines, and cloud security.'
    },
    {
      id: 'CS202',
      code: 'CS202',
      title: 'Object-Oriented Programming (Java)',
      semester: 'Semester 3',
      academicYear: '2024-2025',
      faculty: 'Dr. Sarah Jenkins',
      facultyEmail: 'faculty@courseflow.demo',
      studentsCount: 65,
      completion: 38,
      status: 'Draft',
      credits: 4,
      department: 'Computer Science & Engineering',
      description: 'Encapsulation, inheritance, polymorphism, Java collections framework, exception handling, and concurrent programming.'
    }
  ],
  faculty: [
    {
      id: 'FAC01',
      name: 'Dr. Sarah Jenkins',
      email: 'faculty@courseflow.demo',
      role: 'Associate Professor',
      department: 'Computer Science & Engineering',
      status: 'Active',
      assignedCourses: ['CS301', 'CS302', 'CS401', 'CS202'],
      experienceYears: 11
    },
    {
      id: 'FAC02',
      name: 'Prof. Rajesh Sharma',
      email: 'admin@courseflow.demo',
      role: 'Professor & Dean',
      department: 'Computer Science & Engineering',
      status: 'Active',
      assignedCourses: ['CS303'],
      experienceYears: 24
    },
    {
      id: 'FAC03',
      name: 'Dr. Alan Vance',
      email: 'alan.vance@courseflow.demo',
      role: 'Assistant Professor',
      department: 'Computer Science & Engineering',
      status: 'Active',
      assignedCourses: ['CS304', 'CS305'],
      experienceYears: 6
    },
    {
      id: 'FAC04',
      name: 'Dr. Maya Patel',
      email: 'maya.patel@courseflow.demo',
      role: 'Associate Professor',
      department: 'Computer Science & Engineering',
      status: 'Active',
      assignedCourses: ['CS402'],
      experienceYears: 13
    },
    {
      id: 'FAC05',
      name: 'Prof. David Kim',
      email: 'david.kim@courseflow.demo',
      role: 'Professor',
      department: 'Electronics & Communication',
      status: 'Inactive',
      assignedCourses: [],
      experienceYears: 18
    }
  ],
  students: [
    { id: '22CS001', name: 'Aarav Sharma', email: 'aarav.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS002', name: 'Ananya Iyer', email: 'ananya.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS003', name: 'Devendra Rao', email: 'dev.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS004', name: 'Ishaan Verma', email: 'ishaan.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS005', name: 'Kavya Nair', email: 'kavya.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS006', name: 'Manish Gupta', email: 'manish.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS007', name: 'Neha Kulkarni', email: 'neha.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS008', name: 'Pranav Menon', email: 'pranav.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS009', name: 'Riya Singhania', email: 'riya.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS010', name: 'Siddharth Joshi', email: 'sid.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS011', name: 'Tanvi Deshmukh', email: 'tanvi.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' },
    { id: '22CS012', name: 'Varun Reddy', email: 'varun.22cs@univ.demo', courseId: 'CS301', section: 'A', status: 'Enrolled' }
  ],
  syllabus: {
    'CS301': [
      { unit: 1, title: 'Introduction to Software Engineering & Process Models', hours: 8, outcomes: 'CO1', topics: 'Software crisis, SDLC paradigms, Waterfall, Incremental, Agile Manifesto, Scrum rituals, sprint planning.' },
      { unit: 2, title: 'Requirements Engineering & Domain Modeling', hours: 9, outcomes: 'CO1, CO2', topics: 'Functional & non-functional requirements, elicitation techniques, user stories, SRS IEEE-830, UML use-case diagrams.' },
      { unit: 3, title: 'Architectural Design & Design Patterns', hours: 10, outcomes: 'CO2, CO3', topics: 'Architectural styles (Layered, Microservices, Event-driven), Gang of Four patterns: Factory, Singleton, Observer, Strategy.' },
      { unit: 4, title: 'Software Testing & Quality Assurance', hours: 9, outcomes: 'CO3, CO4', topics: 'Black-box & White-box testing, cyclomatic complexity, unit testing frameworks, integration, regression, CI pipelines.' },
      { unit: 5, title: 'Project Management, Estimation & Maintenance', hours: 9, outcomes: 'CO4, CO5', topics: 'COCOMO estimation, risk analysis, version control git strategies, technical debt, refactoring, maintenance types.' }
    ]
  },
  sessionPlans: {
    'CS301': [
      { id: 'S01', sessionNo: 1, topic: 'Course Orientation & Software Lifecycle Overview', lo: 'CO1', date: '2024-08-05', duration: '60 min', method: 'Interactive Lecture', resources: 'Slides & Syllabus Handout', status: 'Completed' },
      { id: 'S02', sessionNo: 2, topic: 'Waterfall vs Agile Methodologies', lo: 'CO1', date: '2024-08-07', duration: '60 min', method: 'Case Study & Discussion', resources: 'Industry Case Notes', status: 'Completed' },
      { id: 'S03', sessionNo: 3, topic: 'Requirements Elicitation & User Persona Workshop', lo: 'CO1', date: '2024-08-12', duration: '60 min', method: 'Group Activity', resources: 'Miro Board Template', status: 'Completed' },
      { id: 'S04', sessionNo: 4, topic: 'SRS Specification & IEEE 830 Standard', lo: 'CO2', date: '2024-08-14', duration: '60 min', method: 'Problem Solving', resources: 'SRS Sample IEEE-830', status: 'Completed' },
      { id: 'S05', sessionNo: 5, topic: 'UML Use Case and Class Modeling', lo: 'CO2', date: '2024-08-19', duration: '60 min', method: 'Hands-on Lab Prep', resources: 'Draw.io / PlantUML', status: 'Completed' },
      { id: 'S06', sessionNo: 6, topic: 'Architectural Styles & Microservices Paradigm', lo: 'CO3', date: '2024-08-21', duration: '60 min', method: 'Lecture + Diagramming', resources: 'Architecture Reference', status: 'Completed' },
      { id: 'S07', sessionNo: 7, topic: 'Design Patterns: Creational and Structural', lo: 'CO3', date: '2024-08-26', duration: '60 min', method: 'Live Coding Demo', resources: 'GitHub Repository Code', status: 'Completed' },
      { id: 'S08', sessionNo: 8, topic: 'Behavioral Patterns & Observer Pattern Demo', lo: 'CO3', date: '2024-08-28', duration: '60 min', method: 'Peer Programming', resources: 'Design Patterns Reference', status: 'Planned' },
      { id: 'S09', sessionNo: 9, topic: 'Unit Testing Principles & JUnit / Pytest', lo: 'CO4', date: '2024-09-02', duration: '60 min', method: 'Lab Demonstration', resources: 'Sample Test Suite', status: 'Planned' },
      { id: 'S10', sessionNo: 10, topic: 'Continuous Integration & GitHub Actions Workflow', lo: 'CO5', date: '2024-09-04', duration: '60 min', method: 'Demonstration', resources: 'CI YAML Configs', status: 'Planned' }
    ]
  },
  assessments: [
    { id: 'ASM01', courseId: 'CS301', title: 'Continuous Internal Evaluation (CIE-1)', type: 'Internal Exam', maxMarks: 50, weightage: 20, date: '2024-09-15', co: 'CO1, CO2', status: 'Graded' },
    { id: 'ASM02', courseId: 'CS301', title: 'Lab Assignment 1 - UML & Architecture', type: 'Assignment', maxMarks: 25, weightage: 10, date: '2024-09-25', co: 'CO2, CO3', status: 'Graded' },
    { id: 'ASM03', courseId: 'CS301', title: 'Continuous Internal Evaluation (CIE-2)', type: 'Internal Exam', maxMarks: 50, weightage: 20, date: '2024-10-20', co: 'CO3, CO4', status: 'Pending' },
    { id: 'ASM04', courseId: 'CS301', title: 'Term Course Project & Defense', type: 'Project', maxMarks: 50, weightage: 20, date: '2024-11-10', co: 'CO1, CO2, CO3, CO4, CO5', status: 'Pending' },
    { id: 'ASM05', courseId: 'CS301', title: 'Semester End Examination (SEE)', type: 'End Semester', maxMarks: 100, weightage: 30, date: '2024-12-05', co: 'CO1, CO2, CO3, CO4, CO5', status: 'Scheduled' }
  ],
  marks: {
    'ASM01': {
      '22CS001': 44, '22CS002': 48, '22CS003': 39, '22CS004': 42,
      '22CS005': 46, '22CS006': 35, '22CS007': 47, '22CS008': 38,
      '22CS009': 45, '22CS010': 32, '22CS011': 41, '22CS012': 43
    },
    'ASM02': {
      '22CS001': 22, '22CS002': 24, '22CS003': 19, '22CS004': 21,
      '22CS005': 25, '22CS006': 18, '22CS007': 23, '22CS008': 20,
      '22CS009': 24, '22CS010': 17, '22CS011': 22, '22CS012': 21
    }
  },
  // Attendance is strictly Present (P) or Absent (A)
  attendance: {
    'CS301': {
      dates: ['2024-08-05', '2024-08-07', '2024-08-12', '2024-08-14', '2024-08-19', '2024-08-21', '2024-08-26'],
      records: {
        '22CS001': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS002': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS003': ['P', 'A', 'P', 'P', 'P', 'A', 'P'],
        '22CS004': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS005': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS006': ['A', 'P', 'A', 'P', 'A', 'P', 'A'], // Low attendance ~43%
        '22CS007': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS008': ['P', 'P', 'A', 'P', 'P', 'P', 'P'],
        '22CS009': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS010': ['P', 'A', 'P', 'A', 'P', 'P', 'A'], // Borderline ~57%
        '22CS011': ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
        '22CS012': ['P', 'P', 'P', 'P', 'P', 'P', 'P']
      }
    }
  },
  feedback: {
    'CS301': {
      totalResponses: 4,
      averageRating: 4.5,
      categories: [
        { name: 'Course Content & Relevance', rating: 4.6, outOf: 5 },
        { name: 'Teaching Methodology & Clarity', rating: 4.4, outOf: 5 },
        { name: 'Practical Lab & Project Exposure', rating: 4.7, outOf: 5 },
        { name: 'Timely Feedback & Evaluation', rating: 4.2, outOf: 5 }
      ],
      distribution: { 5: 2, 4: 2, 3: 0, 2: 0, 1: 0 },
      comments: [
        { text: 'Hands-on sprint planning and design pattern demos were very practical.', sentiment: 'positive', date: '2024-09-28' },
        { text: 'Clear explanation of software architecture styles. Good pace.', sentiment: 'positive', date: '2024-09-29' },
        { text: 'Assignments were engaging and reflected industry practices.', sentiment: 'positive', date: '2024-10-01' },
        { text: 'Timely grading and feedback on CIE papers.', sentiment: 'neutral', date: '2024-10-02' }
      ]
    }
  },
  outcomes: {
    'CS301': {
      cos: [
        { id: 'CO1', code: 'CO1', text: 'Apply engineering principles and software lifecycle models to formulate project workflows.' },
        { id: 'CO2', code: 'CO2', text: 'Elicit, analyze, and specify software requirements using formal IEEE SRS and UML diagrams.' },
        { id: 'CO3', code: 'CO3', text: 'Design modular software architectures incorporating appropriate Gang of Four design patterns.' },
        { id: 'CO4', code: 'CO4', text: 'Execute systematic verification, unit testing, and continuous integration pipelines.' },
        { id: 'CO5', code: 'CO5', text: 'Estimate project effort, manage risks, and adhere to professional software engineering ethics.' }
      ],
      // Simple 0-3 matrix (0: Unmapped, 1: Low, 2: Medium, 3: High)
      mapping: {
        'CO1': { PO1: 3, PO2: 2, PO3: 1, PO4: 0, PO5: 1, PO6: 0, PO7: 0, PO8: 1, PO9: 2, PO10: 2, PO11: 2, PO12: 2, PSO1: 3, PSO2: 2 },
        'CO2': { PO1: 2, PO2: 3, PO3: 2, PO4: 1, PO5: 1, PO6: 0, PO7: 0, PO8: 1, PO9: 2, PO10: 3, PO11: 1, PO12: 2, PSO1: 3, PSO2: 2 },
        'CO3': { PO1: 3, PO2: 3, PO3: 3, PO4: 2, PO5: 2, PO6: 0, PO7: 0, PO8: 0, PO9: 2, PO10: 2, PO11: 2, PO12: 2, PSO1: 3, PSO2: 3 },
        'CO4': { PO1: 2, PO2: 2, PO3: 3, PO4: 3, PO5: 3, PO6: 0, PO7: 0, PO8: 1, PO9: 2, PO10: 2, PO11: 1, PO12: 2, PSO1: 3, PSO2: 3 },
        'CO5': { PO1: 2, PO2: 1, PO3: 1, PO4: 1, PO5: 1, PO6: 1, PO7: 1, PO8: 3, PO9: 3, PO10: 3, PO11: 3, PO12: 3, PSO1: 2, PSO2: 2 }
      }
    }
  },
  attainment: {
    'CS301': {
      targetBenchmark: 70.0,
      summary: {
        overallAttainment: 77.34,
        directAttainment: 78.5,
        indirectAttainment: 74.2
      },
      overallAverage: 77.34,
      outcomes: [
        { code: 'CO1', target: 70.0, internal: 82.5, external: 81.0, indirect: 80.5, achieved: 81.4, status: 'Meets Target', diff: '+11.4%' },
        { code: 'CO2', target: 70.0, internal: 79.0, external: 78.5, indirect: 80.0, achieved: 78.9, status: 'Meets Target', diff: '+8.9%' },
        { code: 'CO3', target: 70.0, internal: 74.0, external: 72.0, indirect: 76.0, achieved: 73.4, status: 'Meets Target', diff: '+3.4%' },
        { code: 'CO4', target: 75.0, internal: 68.0, external: 66.5, indirect: 72.0, achieved: 68.1, status: 'Below Target', diff: '-6.9%' },
        { code: 'CO5', target: 70.0, internal: 84.0, external: 83.0, indirect: 85.0, achieved: 83.7, status: 'Meets Target', diff: '+13.7%' }
      ],
      poAttainment: {
        'PO1': 2.65, 'PO2': 2.45, 'PO3': 2.80, 'PO4': 2.10, 'PO5': 2.50,
        'PO6': 2.20, 'PO7': 2.30, 'PO8': 2.75, 'PO9': 2.60, 'PO10': 2.40,
        'PO11': 2.55, 'PO12': 2.70, 'PSO1': 2.85, 'PSO2': 2.75
      }
    },
    'CS302': {
      targetBenchmark: 70.0,
      summary: {
        overallAttainment: 82.10,
        directAttainment: 83.0,
        indirectAttainment: 80.0
      },
      overallAverage: 82.10,
      outcomes: [
        { code: 'CO1', target: 70.0, internal: 85.0, external: 84.0, indirect: 82.0, achieved: 83.9, status: 'Meets Target', diff: '+13.9%' },
        { code: 'CO2', target: 70.0, internal: 81.0, external: 80.0, indirect: 80.0, achieved: 80.3, status: 'Meets Target', diff: '+10.3%' },
        { code: 'CO3', target: 70.0, internal: 83.0, external: 82.5, indirect: 81.0, achieved: 82.3, status: 'Meets Target', diff: '+12.3%' },
        { code: 'CO4', target: 70.0, internal: 79.5, external: 81.0, indirect: 80.0, achieved: 80.4, status: 'Meets Target', diff: '+10.4%' },
        { code: 'CO5', target: 70.0, internal: 84.0, external: 83.5, indirect: 83.0, achieved: 83.6, status: 'Meets Target', diff: '+13.6%' }
      ],
      poAttainment: {
        'PO1': 2.80, 'PO2': 2.70, 'PO3': 2.90, 'PO4': 2.40, 'PO5': 2.60,
        'PO6': 2.35, 'PO7': 2.45, 'PO8': 2.80, 'PO9': 2.70, 'PO10': 2.50,
        'PO11': 2.65, 'PO12': 2.75, 'PSO1': 2.90, 'PSO2': 2.80
      }
    }
  },
  // Essential 8-Section Course File Checklist
  courseFiles: {
    'CS301': {
      courseId: 'CS301',
      version: 'v1.0',
      status: 'In Progress', // 'Draft', 'In Progress', 'Completed'
      lastUpdated: '2024-10-15',
      checklist: [
        { id: 'c1', title: 'Course Information & Scope', completed: true, notes: 'Course code, credits, title, and catalog description' },
        { id: 'c2', title: 'Approved Syllabus & Module Units', completed: true, notes: '5 units with topics and allocated contact hours' },
        { id: 'c3', title: 'Teaching Session Plans', completed: true, notes: 'Lecture schedule with dates and teaching methods' },
        { id: 'c4', title: 'Enrolled Student Records', completed: true, notes: '58 active enrolled students registered' },
        { id: 'c5', title: 'Assessment Scheme & Rubrics', completed: true, notes: 'CIE exams, lab assignments, and term project defined' },
        { id: 'c6', title: 'Attendance Records', completed: true, notes: 'Session attendance ledger with student percentages' },
        { id: 'c7', title: 'Student Feedback & Ratings', completed: true, notes: 'Course feedback survey ratings and comments collected' },
        { id: 'c8', title: 'CO-PO/PSO Outcome Mapping', completed: false, notes: 'Course outcomes mapped to program outcomes' }
      ]
    }
  },
  notifications: [
    { id: 'N1', type: 'info', title: 'Course File Status', message: 'CS301 Course File is 88% complete. Finish outcome mapping to complete.', time: '1 hour ago', read: false },
    { id: 'N2', type: 'info', title: 'Session Plan', message: 'Session #8 (Behavioral Patterns) is scheduled next.', time: '3 hours ago', read: false },
    { id: 'N3', type: 'warning', title: 'Attendance Alert', message: 'Student Manish Gupta (22CS006) has attendance below 50%.', time: '1 day ago', read: false },
    { id: 'N4', type: 'success', title: 'Course File Ready', message: 'CS302 Database Management Systems course file is 100% complete.', time: '2 days ago', read: true }
  ]
};

// ==========================================================================
// 2. DATA PERSISTENCE & LOCALSTORAGE ADAPTER
// ==========================================================================
const STORAGE_KEY = 'courseflow_store_v3'; // Bumped for comprehensive attainment analytics

class DataStore {
  constructor() {
    this.data = this.load();
  }

  load() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Could not read from localStorage, using default store.', e);
    }
    this.save(DEFAULT_STORE);
    return JSON.parse(JSON.stringify(DEFAULT_STORE));
  }

  save(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      this.data = data;
    } catch (e) {
      console.warn('Could not save to localStorage.', e);
    }
  }

  reset() {
    this.data = JSON.parse(JSON.stringify(DEFAULT_STORE));
    this.save(this.data);
    return this.data;
  }
}

const db = new DataStore();

// ==========================================================================
// 3. API SERVICE LAYER (Clean, Modular & Student-Friendly)
// ==========================================================================
const apiService = {
  useBackend: false, // Set to true if Flask REST endpoints are enabled

  // Current User
  getCurrentUser() {
    return db.data.currentUser;
  },

  setCurrentUserRole(role) {
    if (role === 'admin') {
      db.data.currentUser = {
        name: 'Prof. Rajesh Sharma',
        email: 'admin@courseflow.demo',
        role: 'admin',
        department: 'Academic Affairs / Dean CSE',
        avatar: 'RS'
      };
    } else {
      db.data.currentUser = {
        name: 'Dr. Sarah Jenkins',
        email: 'faculty@courseflow.demo',
        role: 'faculty',
        department: 'Computer Science & Engineering',
        avatar: 'SJ'
      };
    }
    db.save(db.data);
    return db.data.currentUser;
  },

  // Courses
  async getCourses() {
    if (this.useBackend) {
      const res = await fetch('/api/courses');
      return await res.json();
    }
    return db.data.courses;
  },

  async getCourse(id) {
    if (this.useBackend) {
      const res = await fetch(`/api/courses/${id}`);
      return await res.json();
    }
    return db.data.courses.find(c => c.id === id) || null;
  },

  async saveCourse(course) {
    if (this.useBackend) {
      const method = course.isEdit ? 'PUT' : 'POST';
      const url = course.isEdit ? `/api/courses/${course.id}` : '/api/courses';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(course)
      });
      return await res.json();
    }
    const courses = db.data.courses;
    if (course.isEdit) {
      const index = courses.findIndex(c => c.id === course.id);
      if (index >= 0) {
        courses[index] = { ...courses[index], ...course };
      }
    } else {
      if (courses.some(c => c.code.toUpperCase() === course.code.toUpperCase())) {
        throw new Error(`Course code "${course.code}" already exists.`);
      }
      if (!course.id) course.id = course.code;
      if (!course.completion) course.completion = 0;
      if (!course.status) course.status = 'Draft';
      courses.unshift(course);
    }
    db.save(db.data);
    return course;
  },

  async deleteCourse(id) {
    if (this.useBackend) {
      const res = await fetch(`/api/courses/${id}`, { method: 'DELETE' });
      return await res.json();
    }
    db.data.courses = db.data.courses.filter(c => c.id !== id);
    db.save(db.data);
    return { success: true };
  },

  // Faculty
  async getFaculty() {
    if (this.useBackend) {
      const res = await fetch('/api/faculty');
      return await res.json();
    }
    return db.data.faculty;
  },

  async saveFaculty(fac) {
    const list = db.data.faculty;
    const idx = list.findIndex(f => f.id === fac.id);
    if (idx >= 0) {
      list[idx] = { ...list[idx], ...fac };
    } else {
      if (!fac.id) fac.id = 'FAC' + (list.length + 1).toString().padStart(2, '0');
      list.push(fac);
    }
    db.save(db.data);
    return fac;
  },

  // Students
  async getStudents(courseId) {
    if (courseId) {
      return db.data.students.filter(s => s.courseId === courseId);
    }
    return db.data.students;
  },

  async saveStudent(student) {
    const list = db.data.students;
    const idx = list.findIndex(s => s.id === student.id);
    if (idx >= 0) {
      list[idx] = { ...list[idx], ...student };
    } else {
      list.push(student);
    }
    db.save(db.data);
    return student;
  },

  async deleteStudent(id) {
    db.data.students = db.data.students.filter(s => s.id !== id);
    db.save(db.data);
    return { success: true };
  },

  // Syllabus
  async getSyllabus(courseId) {
    return db.data.syllabus[courseId] || [
      { unit: 1, title: 'Introduction & Foundations', hours: 8, outcomes: 'CO1', topics: 'Fundamental concepts, principles, and problem definitions.' }
    ];
  },

  async saveSyllabus(courseId, units) {
    db.data.syllabus[courseId] = units;
    db.save(db.data);
    return units;
  },

  // Session Plans
  async getSessionPlans(courseId) {
    return db.data.sessionPlans[courseId] || [];
  },

  async saveSessionPlan(courseId, session) {
    if (!db.data.sessionPlans[courseId]) db.data.sessionPlans[courseId] = [];
    const list = db.data.sessionPlans[courseId];
    const idx = list.findIndex(s => s.id === session.id);
    if (idx >= 0) {
      list[idx] = { ...list[idx], ...session };
    } else {
      if (!session.id) session.id = 'S' + (list.length + 1).toString().padStart(2, '0');
      list.push(session);
    }
    db.save(db.data);
    return session;
  },

  async deleteSessionPlan(courseId, sessionId) {
    if (db.data.sessionPlans[courseId]) {
      db.data.sessionPlans[courseId] = db.data.sessionPlans[courseId].filter(s => s.id !== sessionId);
      db.save(db.data);
    }
    return { success: true };
  },

  // Assessments & Marks
  async getAssessments(courseId) {
    if (courseId) {
      return db.data.assessments.filter(a => a.courseId === courseId);
    }
    return db.data.assessments;
  },

  async saveAssessment(asm) {
    const list = db.data.assessments;
    const idx = list.findIndex(a => a.id === asm.id);
    if (idx >= 0) {
      list[idx] = { ...list[idx], ...asm };
    } else {
      if (!asm.id) asm.id = 'ASM' + (list.length + 1).toString().padStart(2, '0');
      list.push(asm);
    }
    db.save(db.data);
    return asm;
  },

  async deleteAssessment(id) {
    db.data.assessments = db.data.assessments.filter(a => a.id !== id);
    db.save(db.data);
    return { success: true };
  },

  async getMarks(assessmentId) {
    return db.data.marks[assessmentId] || {};
  },

  async saveMarks(assessmentId, marksMap) {
    db.data.marks[assessmentId] = marksMap;
    db.save(db.data);
    return marksMap;
  },

  // Attendance (Present / Absent)
  async getAttendance(courseId) {
    return db.data.attendance[courseId] || { dates: [], records: {} };
  },

  async saveAttendance(courseId, attData) {
    db.data.attendance[courseId] = attData;
    db.save(db.data);
    return attData;
  },

  // Feedback (Rating 1-5 and optional comment)
  async getFeedback(courseId) {
    return db.data.feedback[courseId] || {
      totalResponses: 0,
      averageRating: 0,
      categories: [],
      distribution: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 },
      comments: []
    };
  },

  async addFeedback(courseId, rating, comment) {
    if (!db.data.feedback[courseId]) {
      db.data.feedback[courseId] = {
        totalResponses: 0,
        averageRating: 0,
        categories: [
          { name: 'Course Content & Relevance', rating: 4.5, outOf: 5 },
          { name: 'Teaching Methodology', rating: 4.5, outOf: 5 },
          { name: 'Practical Exposure', rating: 4.5, outOf: 5 }
        ],
        distribution: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 },
        comments: []
      };
    }
    const fb = db.data.feedback[courseId];
    const numRating = parseInt(rating, 10) || 5;
    fb.totalResponses += 1;
    fb.distribution[numRating] = (fb.distribution[numRating] || 0) + 1;

    // Recalculate average rating
    let totalScore = 0;
    Object.keys(fb.distribution).forEach(star => {
      totalScore += parseInt(star, 10) * (fb.distribution[star] || 0);
    });
    fb.averageRating = parseFloat((totalScore / fb.totalResponses).toFixed(1));

    if (comment && comment.trim()) {
      fb.comments.unshift({
        text: comment.trim(),
        sentiment: numRating >= 4 ? 'positive' : (numRating === 3 ? 'neutral' : 'constructive'),
        date: new Date().toISOString().split('T')[0]
      });
    }

    db.save(db.data);
    return fb;
  },

  // Outcomes & Mapping
  async getOutcomes(courseId) {
    return db.data.outcomes[courseId] || { cos: [], mapping: {} };
  },

  async saveOutcomes(courseId, data) {
    // M5-TC04: Restrict correlation values to the range 0-3
    if (data && data.mapping) {
      for (const co in data.mapping) {
        for (const target in data.mapping[co]) {
          const val = parseInt(data.mapping[co][target], 10);
          if (isNaN(val) || val < 0 || val > 3) {
            throw new Error(`Correlation level for ${co} -> ${target} must be between 0 and 3.`);
          }
          data.mapping[co][target] = val;
        }
      }
    }
    db.data.outcomes[courseId] = data;
    db.save(db.data);
    return data;
  },

  // Attainment
  async getAttainment(courseId) {
    if (db.data.attainment && db.data.attainment[courseId]) {
      return db.data.attainment[courseId];
    }
    // Return CS301 attainment as robust default so page never renders empty
    return (db.data.attainment && db.data.attainment['CS301']) || DEFAULT_STORE.attainment['CS301'];
  },

  // Course File (8 Essential Sections)
  async getCourseFile(courseId) {
    let cf = db.data.courseFiles[courseId];
    if (!cf) {
      cf = {
        courseId,
        version: 'v1.0',
        status: 'Draft',
        lastUpdated: new Date().toISOString().split('T')[0],
        checklist: DEFAULT_STORE.courseFiles['CS301'].checklist.map(item => ({ ...item, completed: false }))
      };
      db.data.courseFiles[courseId] = cf;
      db.save(db.data);
    }
    return cf;
  },

  async updateCourseFileStatus(courseId, status) {
    const cf = await this.getCourseFile(courseId);
    cf.status = status;
    cf.lastUpdated = new Date().toISOString().split('T')[0];
    db.data.courseFiles[courseId] = cf;

    const c = db.data.courses.find(item => item.id === courseId);
    if (c) c.status = status;
    db.save(db.data);
    return cf;
  },

  async updateChecklistItem(courseId, checkId, completed) {
    const cf = await this.getCourseFile(courseId);
    const item = cf.checklist.find(i => i.id === checkId);
    if (item) {
      item.completed = completed;
      const total = cf.checklist.length;
      const done = cf.checklist.filter(i => i.completed).length;
      const pct = Math.round((done / total) * 100);

      // Update course file status
      if (pct === 100) {
        cf.status = 'Completed';
      } else if (pct > 0) {
        cf.status = 'In Progress';
      } else {
        cf.status = 'Draft';
      }

      // Sync with course catalog
      const c = db.data.courses.find(item => item.id === courseId);
      if (c) {
        c.completion = pct;
        c.status = cf.status;
      }
      db.save(db.data);
    }
    return cf;
  },

  // AI Assistant Handout Summarizer (Demonstration Handler)
  async summarizeHandout(fileData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          courseCode: 'CS301',
          courseTitle: 'Software Engineering',
          topicsIdentified: [
            'Software Development Lifecycle (Agile & Waterfall)',
            'Requirements Engineering & IEEE SRS Document',
            'Software Architecture & Common Design Patterns',
            'Unit Testing Principles & Verification',
            'Project Planning, Effort Estimation & Version Control'
          ],
          suggestedOutcomes: [
            'CO1: Explain software lifecycle models and agile development practices.',
            'CO2: Formulate functional and non-functional requirements specifications.',
            'CO3: Apply modular architecture and design patterns to software problems.',
            'CO4: Write and execute unit tests to ensure software quality.'
          ],
          recommendedHours: 45,
          extractedSummary: 'This course provides core foundations in engineering reliable software systems, covering lifecycle models, requirements analysis, modular architectural design, testing methodologies, and project collaboration.'
        });
      }, 700);
    });
  },

  // Notifications
  getNotifications() {
    return db.data.notifications;
  },

  markNotificationsRead() {
    db.data.notifications.forEach(n => n.read = true);
    db.save(db.data);
  }
};

// ==========================================================================
// 4. GLOBAL UI UTILITIES
// ==========================================================================
function showToast(message, type = 'info', title = 'CourseFlow Notification') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const iconMap = {
    success: 'bi-check-circle-fill text-success',
    warning: 'bi-exclamation-triangle-fill text-warning',
    danger: 'bi-x-circle-fill text-danger',
    info: 'bi-info-circle-fill text-primary'
  };

  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center show shadow-lg border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" style="background:#fff; border-radius: 12px; min-width: 280px;">
      <div class="d-flex p-3 align-items-start gap-2">
        <i class="bi ${iconMap[type] || iconMap.info} fs-5 mt-n1"></i>
        <div class="flex-grow-1">
          <div class="fw-semibold text-dark fs-6">${title}</div>
          <div class="text-secondary small mt-1">${message}</div>
        </div>
        <button type="button" class="btn-close ms-2" data-bs-dismiss="toast" aria-label="Close" onclick="document.getElementById('${toastId}').remove()"></button>
      </div>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', toastHtml);

  setTimeout(() => {
    const el = document.getElementById(toastId);
    if (el) el.remove();
  }, 4000);
}

function confirmAction(message, onConfirm, title = 'Confirm Action') {
  if (window.confirm(`${title}\n\n${message}`)) {
    onConfirm();
  }
}

// Sidebar toggle & mobile drawer
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const sidebar = document.querySelector('.app-sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
      let backdrop = document.querySelector('.sidebar-backdrop');
      if (sidebar.classList.contains('show')) {
        if (!backdrop) {
          backdrop = document.createElement('div');
          backdrop.className = 'sidebar-backdrop';
          backdrop.addEventListener('click', () => {
            sidebar.classList.remove('show');
            backdrop.remove();
          });
          document.body.appendChild(backdrop);
        }
      } else if (backdrop) {
        backdrop.remove();
      }
    });
  }

  // Demo Role Switcher
  const roleSelects = document.querySelectorAll('.demo-role-switcher');
  roleSelects.forEach(select => {
    select.addEventListener('change', (e) => {
      const newRole = e.target.value;
      apiService.setCurrentUserRole(newRole);
      fetch('/api/switch-role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole })
      }).finally(() => {
        showToast(`Switched active view to ${newRole.toUpperCase()}`, 'info', 'Role Switch');
        setTimeout(() => window.location.reload(), 300);
      });
    });
  });

  // Notifications
  const notifDropdown = document.getElementById('notificationsDropdownMenu');
  if (notifDropdown) {
    renderNotificationsDropdown(notifDropdown);
  }

  // Active Course Selector
  const globalCourseSelect = document.getElementById('globalCourseSelect');
  if (globalCourseSelect) {
    const storedCourse = localStorage.getItem('cf_selected_course') || 'CS301';
    globalCourseSelect.value = storedCourse;
    globalCourseSelect.addEventListener('change', (e) => {
      localStorage.setItem('cf_selected_course', e.target.value);
      window.location.reload();
    });
  }
});

function renderNotificationsDropdown(menuEl) {
  const notifs = apiService.getNotifications();
  const unreadCount = notifs.filter(n => !n.read).length;
  const badge = document.getElementById('notificationBadgeCount');
  if (badge) {
    if (unreadCount > 0) {
      badge.textContent = unreadCount;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  let html = `
    <div class="p-3 border-bottom d-flex align-items-center justify-content-between bg-light rounded-top">
      <div class="fw-bold text-dark">Notifications</div>
      <button class="btn btn-sm btn-link p-0 text-decoration-none small text-primary" onclick="markAllNotifsRead()">Mark all as read</button>
    </div>
    <div class="notification-list" style="max-height: 320px; overflow-y: auto;">
  `;

  if (notifs.length === 0) {
    html += `<div class="p-4 text-center text-muted small">No notifications at this time.</div>`;
  } else {
    notifs.forEach(n => {
      const iconMap = {
        warning: 'bi-exclamation-circle text-warning bg-warning-subtle',
        danger: 'bi-shield-x text-danger bg-danger-subtle',
        success: 'bi-check2-circle text-success bg-success-subtle',
        info: 'bi-bell text-primary bg-primary-subtle'
      };
      html += `
        <div class="notification-item ${n.read ? '' : 'unread'}">
          <div class="notification-icon-wrap ${iconMap[n.type] || 'bi-bell'}">
            <i class="bi ${n.type === 'danger' ? 'bi-shield-x' : n.type === 'warning' ? 'bi-exclamation-triangle' : n.type === 'success' ? 'bi-check-lg' : 'bi-bell'}"></i>
          </div>
          <div class="flex-grow-1">
            <div class="fw-semibold text-dark small">${n.title}</div>
            <div class="text-secondary small" style="font-size: 0.78rem;">${n.message}</div>
            <div class="text-muted small mt-1" style="font-size: 0.7rem;"><i class="bi bi-clock me-1"></i>${n.time}</div>
          </div>
        </div>
      `;
    });
  }

  html += `
    </div>
    <div class="p-2 border-top text-center bg-light rounded-bottom">
      <span class="text-muted small" style="font-size: 0.75rem;">CourseFlow Notifications</span>
    </div>
  `;
  menuEl.innerHTML = html;
}

window.markAllNotifsRead = function() {
  apiService.markNotificationsRead();
  const notifDropdown = document.getElementById('notificationsDropdownMenu');
  if (notifDropdown) renderNotificationsDropdown(notifDropdown);
  showToast('All notifications marked as read', 'success');
};

function renderStatusBadge(status) {
  const norm = (status || '').toLowerCase().replace(/\s+/g, '');
  let badgeClass = 'badge-status-draft';
  let icon = 'bi-circle';

  if (norm.includes('completed') || norm.includes('approved') || norm.includes('meets')) {
    badgeClass = 'badge-status-completed';
    icon = 'bi-check-circle-fill';
  } else if (norm.includes('progress') || norm.includes('review')) {
    badgeClass = 'badge-status-inprogress';
    icon = 'bi-hourglass-split';
  } else if (norm.includes('warning') || norm.includes('below') || norm.includes('attention')) {
    badgeClass = 'badge-status-warning';
    icon = 'bi-exclamation-triangle-fill';
  }

  return `<span class="badge-status ${badgeClass}"><i class="bi ${icon}"></i> ${status}</span>`;
}

window.CourseFlow = {
  db,
  apiService,
  showToast,
  confirmAction,
  renderStatusBadge
};
