"""
Curriculum, Institutional Outcomes & CO-PO Mapping Models
Matches BML Munjal University & School of Engineering & Technology OBE Structure.
"""

from database import db

class UniversityInfo(db.Model):
    __tablename__ = 'university_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default='BML Munjal University')
    vision = db.Column(db.Text, nullable=False)
    mission = db.Column(db.Text, nullable=False)

class SchoolInfo(db.Model):
    __tablename__ = 'school_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default='School of Engineering & Technology')
    vision = db.Column(db.Text, nullable=False)
    mission = db.Column(db.Text, nullable=False)

class GraduateAttribute(db.Model):
    __tablename__ = 'graduate_attributes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)  # GA1..GA7
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

class PEO(db.Model):
    __tablename__ = 'peos'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)  # PEO 1..PEO 4
    description = db.Column(db.Text, nullable=False)

class ProgramOutcome(db.Model):
    __tablename__ = 'program_outcomes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)  # PO1..PO12
    title = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=False)

class ProgramSpecificOutcome(db.Model):
    __tablename__ = 'program_specific_outcomes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)  # PSO1..PSO4
    title = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=False)

class CourseOutcome(db.Model):
    __tablename__ = 'course_outcomes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)  # CO1, CO2, CO3
    description = db.Column(db.Text, nullable=False)
    mapped_component = db.Column(db.String(100), default='Skill Development')  # Skill Development, Employability, Entrepreneurship
    target_benchmark = db.Column(db.Float, default=70.0)  # e.g., 70%
    class_average = db.Column(db.Float, default=0.0)
    attainment_level = db.Column(db.Integer, default=3)  # 1, 2, 3
    associated_activities = db.Column(db.Text, nullable=True)

    course_rel = db.relationship('Course', back_populates='outcomes')
    mappings = db.relationship('CO_PO_Mapping', back_populates='outcome_rel', cascade='all, delete-orphan')

    def to_dict(self):
        diff = round(self.class_average - self.target_benchmark, 1) if self.class_average else 0.0
        status = 'Attained' if self.class_average >= self.target_benchmark else ('In Progress' if self.class_average > 0 else 'Pending')
        return {
            'id': self.id,
            'courseId': self.course_id,
            'code': self.code,
            'description': self.description,
            'mappedComponent': self.mapped_component,
            'targetBenchmark': f"{self.target_benchmark}%",
            'classAverageScore': f"{self.class_average}%" if self.class_average else "N/A",
            'difference': f"{diff:+.1f}%" if self.class_average else "0.0%",
            'status': status,
            'attainmentLevel': self.attainment_level,
            'associatedActivities': self.associated_activities
        }

class CO_PO_Mapping(db.Model):
    __tablename__ = 'co_po_mappings'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    outcome_id = db.Column(db.Integer, db.ForeignKey('course_outcomes.id'), nullable=False)
    outcome_code = db.Column(db.String(20), nullable=False)
    target_code = db.Column(db.String(20), nullable=False)  # PO1..PO12, PSO1..PSO4
    level = db.Column(db.Integer, default=0)  # 0=None, 1=Low, 2=Moderate, 3=High

    outcome_rel = db.relationship('CourseOutcome', back_populates='mappings')
