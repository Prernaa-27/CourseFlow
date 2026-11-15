"""
Student Feedback, Interventions & Outcome Attainment Models
"""

from datetime import datetime
from database import db

class StudentFeedback(db.Model):
    __tablename__ = 'student_feedback'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    feedback_type = db.Column(db.String(50), default='Mid-Term')  # Mid-Term, Exit Survey, Class Committee
    rating_co1 = db.Column(db.Float, default=4.0)  # Scale 1-5
    rating_co2 = db.Column(db.Float, default=4.0)
    rating_co3 = db.Column(db.Float, default=4.0)
    overall_rating = db.Column(db.Float, default=4.0)
    comments = db.Column(db.Text, nullable=True)
    corrective_actions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course_rel = db.relationship('Course', back_populates='feedback_entries')

class Intervention(db.Model):
    __tablename__ = 'interventions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    category = db.Column(db.String(50), default='Slow Performer')  # Slow Performer, Advanced Learner
    reason = db.Column(db.String(255), nullable=False)
    action_taken = db.Column(db.Text, nullable=False)  # Remedial session, retest, research paper study, etc.
    outcome_observed = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='In Progress')  # Planned, In Progress, Resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course_rel = db.relationship('Course', back_populates='interventions')

class COAttainmentRecord(db.Model):
    __tablename__ = 'co_attainment_records'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    outcome_code = db.Column(db.String(20), nullable=False)  # CO1, CO2, CO3
    direct_attainment = db.Column(db.Float, default=0.0)  # CIE + SEE weighted average
    indirect_attainment = db.Column(db.Float, default=0.0)  # Exit survey average
    overall_attainment = db.Column(db.Float, default=0.0)  # 80% Direct + 20% Indirect
    students_evaluated = db.Column(db.Integer, default=58)
    students_attained = db.Column(db.Integer, default=50)
    attainment_percentage = db.Column(db.Float, default=86.2)
    attainment_level = db.Column(db.Integer, default=3)  # 1 (<60%), 2 (60-70%), 3 (>=70%)
    target_benchmark = db.Column(db.Float, default=70.0)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'outcomeCode': self.outcome_code,
            'directAttainment': f"{self.direct_attainment:.1f}%",
            'indirectAttainment': f"{self.indirect_attainment:.1f}%",
            'overallAttainment': f"{self.overall_attainment:.1f}%",
            'studentsEvaluated': self.students_evaluated,
            'studentsAttained': self.students_attained,
            'percentage': f"{self.attainment_percentage:.1f}%",
            'level': self.attainment_level,
            'target': f"{self.target_benchmark:.1f}%",
            'status': 'Attained' if self.attainment_percentage >= self.target_benchmark else 'Not Attained'
        }
