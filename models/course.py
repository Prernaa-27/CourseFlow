"""
Course & Course File Section Models
Implements 25-section course file management structure matching official university requirements.
"""

from datetime import datetime
from database import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.String(50), primary_key=True)  # e.g., 'CSE3005' or 'CS301'
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, default=3)
    lecture_hours = db.Column(db.Integer, default=2)
    tutorial_hours = db.Column(db.Integer, default=0)
    practical_hours = db.Column(db.Integer, default=2)
    
    semester = db.Column(db.String(50), default='Semester 4')
    batch = db.Column(db.String(50), default='Batch 2024')
    academic_year = db.Column(db.String(50), default='2026-27')
    semester_duration = db.Column(db.String(100), default='27th July 2025 to 28th Nov 2026')
    
    department = db.Column(db.String(100), default='Computer Science & Engineering')
    school = db.Column(db.String(100), default='School of Engineering & Technology')
    university = db.Column(db.String(100), default='BML Munjal University')
    
    aim = db.Column(db.Text, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='In Progress')  # In Progress, Completed
    
    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    coordinator_rel = db.relationship('User', back_populates='courses_coordinated', foreign_keys=[coordinator_id])
    
    # Relationships
    faculty_assignments = db.relationship('FacultyAssignment', back_populates='course_rel', cascade='all, delete-orphan')
    sections = db.relationship('CourseFileSection', back_populates='course_rel', cascade='all, delete-orphan', order_by='CourseFileSection.section_number')
    outcomes = db.relationship('CourseOutcome', back_populates='course_rel', cascade='all, delete-orphan', order_by='CourseOutcome.code')
    modules = db.relationship('SyllabusModule', back_populates='course_rel', cascade='all, delete-orphan', order_by='SyllabusModule.module_number')
    enrolments = db.relationship('StudentEnrolment', back_populates='course_rel', cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', back_populates='course_rel', cascade='all, delete-orphan')
    timetable_entries = db.relationship('TimetableEntry', back_populates='course_rel', cascade='all, delete-orphan')
    feedback_entries = db.relationship('StudentFeedback', back_populates='course_rel', cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', back_populates='course_rel', cascade='all, delete-orphan')
    documents = db.relationship('CourseDocument', back_populates='course_rel', cascade='all, delete-orphan')

    def calculate_completion(self):
        """Calculate overall course file completion percentage across 25 sections."""
        if not self.sections:
            return 84  # Default benchmark for demonstration
        completed = sum(1 for s in self.sections if s.status == 'Completed')
        return round((completed / len(self.sections)) * 100)

    @property
    def completion(self):
        return self.calculate_completion()

    @property
    def academicYear(self):
        return self.academic_year

    @property
    def faculty(self):
        return self.coordinator_rel.name if self.coordinator_rel else 'Dr. Shilpa Mahajan'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'semester': self.semester,
            'batch': self.batch,
            'academicYear': self.academic_year,
            'semesterDuration': self.semester_duration,
            'credits': self.credits,
            'contactHours': f"{self.lecture_hours} Hours Theory & {self.practical_hours} Hours Lab per week",
            'department': self.department,
            'school': self.school,
            'university': self.university,
            'aim': self.aim,
            'overview': self.overview,
            'description': self.description,
            'status': self.status,
            'completion': self.calculate_completion(),
            'studentsCount': len(self.enrolments) if self.enrolments else 0,
            'faculty': self.coordinator_rel.name if self.coordinator_rel else 'Faculty Coordinator',
            'facultyEmail': self.coordinator_rel.email if self.coordinator_rel else ''
        }

class FacultyAssignment(db.Model):
    __tablename__ = 'faculty_assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_in_course = db.Column(db.String(50), default='Instructor')  # Coordinator, Instructor, Lab Instructor
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    course_rel = db.relationship('Course', back_populates='faculty_assignments')
    faculty_rel = db.relationship('User', back_populates='faculty_assignments')

class CourseFileSection(db.Model):
    __tablename__ = 'course_file_sections'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    section_number = db.Column(db.Integer, nullable=False)  # 1 to 25
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Not Started')  # Not Started, In Progress, Completed, Needs Review
    notes = db.Column(db.Text, nullable=True)
    content_payload = db.Column(db.Text, nullable=True)  # Structured JSON string when needed
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    course_rel = db.relationship('Course', back_populates='sections')
    documents = db.relationship('CourseDocument', back_populates='section_rel', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'courseId': self.course_id,
            'sectionNumber': self.section_number,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'notes': self.notes,
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,
            'documentsCount': len(self.documents) if self.documents else 0
        }

class CourseDocument(db.Model):
    __tablename__ = 'course_documents'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('course_file_sections.id'), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size_bytes = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    course_rel = db.relationship('Course', back_populates='documents')
    section_rel = db.relationship('CourseFileSection', back_populates='documents')

    def to_dict(self):
        return {
            'id': self.id,
            'courseId': self.course_id,
            'fileName': self.file_name,
            'fileType': self.file_type,
            'fileSizeBytes': self.file_size_bytes,
            'uploadedAt': self.uploaded_at.strftime('%Y-%m-%d %H:%M') if self.uploaded_at else None
        }
