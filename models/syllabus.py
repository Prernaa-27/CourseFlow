"""
Syllabus Modules, Session Plans & Timetable Models
Configured for CSE3005 (48 sessions: 31 Theory + 17 Lab across 7 Modules).
"""

from database import db

class SyllabusModule(db.Model):
    __tablename__ = 'syllabus_modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    module_number = db.Column(db.Integer, nullable=False)  # 1 to 7
    title = db.Column(db.String(255), nullable=False)
    detailed_topics = db.Column(db.Text, nullable=False)
    mapped_cos = db.Column(db.String(50), default='CO1')
    theory_hours = db.Column(db.Integer, default=4)
    lab_hours = db.Column(db.Integer, default=2)
    total_sessions = db.Column(db.Integer, default=6)
    readings = db.Column(db.Text, nullable=True)
    pedagogy = db.Column(db.String(100), default='Interactive Lecture & Hands-on Lab')

    course_rel = db.relationship('Course', back_populates='modules')
    units = db.relationship('SyllabusUnit', back_populates='module_rel', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'moduleNumber': self.module_number,
            'title': self.title,
            'detailedTopics': self.detailed_topics,
            'mappedCOs': self.mapped_cos,
            'theoryHours': self.theory_hours,
            'labHours': self.lab_hours,
            'totalSessions': self.total_sessions,
            'pedagogy': self.pedagogy
        }

class SyllabusUnit(db.Model):
    __tablename__ = 'syllabus_units'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('syllabus_modules.id'), nullable=False)
    unit_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    topics = db.Column(db.Text, nullable=True)

    module_rel = db.relationship('SyllabusModule', back_populates='units')

class SessionPlan(db.Model):
    __tablename__ = 'session_plans'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    session_number = db.Column(db.Integer, nullable=False)  # 1 to 48
    module_number = db.Column(db.Integer, default=1)
    session_type = db.Column(db.String(20), default='Theory')  # Theory, Lab
    topic = db.Column(db.String(255), nullable=False)
    mapped_co = db.Column(db.String(20), default='CO1')
    teaching_method = db.Column(db.String(100), default='Interactive Lecture')
    scheduled_date = db.Column(db.String(50), nullable=True)
    actual_date = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='Completed')  # Completed, Scheduled, Delayed
    remarks = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sessionNumber': self.session_number,
            'moduleNumber': self.module_number,
            'sessionType': self.session_type,
            'topic': self.topic,
            'mappedCO': self.mapped_co,
            'teachingMethod': self.teaching_method,
            'scheduledDate': self.scheduled_date,
            'actualDate': self.actual_date,
            'status': self.status,
            'remarks': self.remarks
        }

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(50), db.ForeignKey('courses.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)  # Monday, Wednesday, etc.
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    session_type = db.Column(db.String(20), default='Theory')
    room_location = db.Column(db.String(100), default='E2-401')
    faculty_name = db.Column(db.String(100), default='Dr. Shilpa Mahajan')

    course_rel = db.relationship('Course', back_populates='timetable_entries')

    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day_of_week,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'sessionType': self.session_type,
            'room': self.room_location,
            'faculty': self.faculty_name
        }
