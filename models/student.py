"""
Student, Enrolment, Assessment, Marks & Attendance Models
Adheres to Phase 12 Data Integrity (Clean DEMO DATA for CSE3005; strict separation from CSE2724).
"""

from datetime import datetime
from database import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    batch = db.Column(db.String(50), default='Batch 2024')
    semester = db.Column(db.String(50), default='Semester 4')
    section = db.Column(db.String(10), default='A')
    department = db.Column(db.String(100), default='Computer Science & Engineering')
    is_demo_data = db.Column(db.Boolean, default=True)  # Clearly labels demo vs actual data

    enrolments = db.relationship('StudentEnrolment', back_populates='student_rel', cascade='all, delete-orphan')
    marks = db.relationship('StudentMark', back_populates='student_rel', cascade='all, delete-orphan')
    attendance = db.relationship('AttendanceRecord', back_populates='student_rel', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'rollNo': self.roll_no,
            'name': self.name,
            'email': self.email,
            'batch': self.batch,
            'semester': self.semester,
            'section': self.section,
            'department': self.department,
            'isDemoData': self.is_demo_data
        }

class StudentEnrolment(db.Model):
    __tablename__ = 'student_enrolments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Active')

    student_rel = db.relationship('Student', back_populates='enrolments')
    course_rel = db.relationship('Course', back_populates='enrolments')

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Lab Assessment, Quiz, End Semester Examination
    assessment_type = db.Column(db.String(50), default='Internal')  # Internal CIE, External SEE
    weightage_percent = db.Column(db.Float, default=40.0)  # 40%, 20%, 40%
    max_marks = db.Column(db.Float, default=100.0)
    evaluation_schedule = db.Column(db.String(150), nullable=True)
    mapped_cos = db.Column(db.String(100), default='CO1, CO2, CO3')
    rubrics = db.Column(db.Text, nullable=True)

    course_rel = db.relationship('Course', back_populates='assessments')
    components = db.relationship('AssessmentComponent', back_populates='assessment_rel', cascade='all, delete-orphan')
    student_marks = db.relationship('StudentMark', back_populates='assessment_rel', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'courseId': self.course_id,
            'name': self.name,
            'type': self.assessment_type,
            'weightage': f"{self.weightage_percent}%",
            'maxMarks': self.max_marks,
            'schedule': self.evaluation_schedule,
            'mappedCOs': self.mapped_cos,
            'rubrics': self.rubrics
        }

class AssessmentComponent(db.Model):
    __tablename__ = 'assessment_components'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Lab Evaluation 1, Lab Evaluation 2, Quiz 1, etc.
    max_marks = db.Column(db.Float, default=25.0)
    weightage_percent = db.Column(db.Float, default=10.0)

    assessment_rel = db.relationship('Assessment', back_populates='components')

class StudentMark(db.Model):
    __tablename__ = 'student_marks'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    marks_obtained = db.Column(db.Float, default=0.0)
    max_marks = db.Column(db.Float, default=100.0)
    grade = db.Column(db.String(5), default='B')
    is_weak_student = db.Column(db.Boolean, default=False)  # Scored below 40%

    student_rel = db.relationship('Student', back_populates='marks')
    assessment_rel = db.relationship('Assessment', back_populates='student_marks')

    def to_dict(self):
        pct = round((self.marks_obtained / self.max_marks) * 100, 1) if self.max_marks else 0
        return {
            'id': self.id,
            'courseId': self.course_id,
            'studentId': self.student_id,
            'assessmentId': self.assessment_id,
            'rollNo': self.student_rel.roll_no if self.student_rel else '',
            'studentName': self.student_rel.name if self.student_rel else '',
            'assessment': self.assessment_rel.name if self.assessment_rel else '',
            'marksObtained': self.marks_obtained,
            'maxMarks': self.max_marks,
            'percentage': f"{pct}%",
            'grade': self.grade,
            'isWeak': self.is_weak_student
        }

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_classes = db.Column(db.Integer, default=48)  # 48 sessions
    attended_classes = db.Column(db.Integer, default=40)
    percentage = db.Column(db.Float, default=83.3)
    status = db.Column(db.String(50), default='Good')  # 'Good', 'Warning (75-80%)', 'Critical (<75%)'

    student_rel = db.relationship('Student', back_populates='attendance')

    def update_status(self):
        if self.total_classes > 0:
            self.percentage = round((self.attended_classes / self.total_classes) * 100, 1)
        else:
            self.percentage = 0.0
        if self.percentage < 75.0:
            self.status = 'Critical (<75%)'
        elif self.percentage < 80.0:
            self.status = 'Warning'
        else:
            self.status = 'Eligible'

    def to_dict(self):
        return {
            'id': self.id,
            'rollNo': self.student_rel.roll_no if self.student_rel else '',
            'name': self.student_rel.name if self.student_rel else '',
            'totalClasses': self.total_classes,
            'attendedClasses': self.attended_classes,
            'percentage': f"{self.percentage}%",
            'status': self.status,
            'isShortage': self.percentage < 75.0
        }
