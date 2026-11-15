"""
Software Engineering Lifecycle & Capstone Models
Includes: Requirements/SRS with MoSCoW, Architecture Diagrams, Test Management, and SPM (Gantt/PERT/CPM).
"""

from datetime import datetime
from database import db

class ProjectRequirement(db.Model):
    __tablename__ = 'project_requirements'

    id = db.Column(db.Integer, primary_key=True)
    req_id = db.Column(db.String(20), unique=True, nullable=False)  # FR-01, NFR-01
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Functional')  # Functional, Non-Functional
    moscow = db.Column(db.String(20), default='Must Have')  # Must Have, Should Have, Could Have, Won't Have
    status = db.Column(db.String(50), default='Implemented')  # Proposed, In Progress, Implemented, Verified
    stakeholder = db.Column(db.String(100), default='Faculty / Course Coordinator')
    acceptance_criteria = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'reqId': self.req_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'moscow': self.moscow,
            'status': self.status,
            'stakeholder': self.stakeholder,
            'acceptanceCriteria': self.acceptance_criteria
        }

class ArchitectureDiagram(db.Model):
    __tablename__ = 'architecture_diagrams'

    id = db.Column(db.Integer, primary_key=True)
    diagram_type = db.Column(db.String(50), nullable=False, unique=True)  # Use Case, Class, Sequence, etc.
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    mermaid_code = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    components_involved = db.Column(db.String(255), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.diagram_type,
            'title': self.title,
            'description': self.description,
            'mermaidCode': self.mermaid_code,
            'imageUrl': self.image_url,
            'components': self.components_involved,
            'lastUpdated': self.last_updated.strftime('%Y-%m-%d') if self.last_updated else None
        }

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    __test__ = False  # Prevent PyTest from treating this ORM model as a test suite

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.String(30), unique=True, nullable=False)  # M1-TC01, QA-SEC-01, etc.
    module = db.Column(db.String(100), nullable=False)  # Auth, Course File, Handout, Attainment, etc.
    test_type = db.Column(db.String(50), default='System')  # Unit, Integration, System, Regression, Performance, Security, User Acceptance
    test_scenario = db.Column(db.String(255), nullable=False)
    preconditions = db.Column(db.Text, nullable=True)
    test_inputs = db.Column(db.Text, nullable=True)
    expected_output = db.Column(db.Text, nullable=False)
    actual_output = db.Column(db.Text, nullable=True)
    test_result = db.Column(db.String(20), default='Pass')  # Pass, Fail, Blocked, Not Executed
    severity = db.Column(db.String(20), default='Medium')  # Critical, High, Medium, Low
    tester = db.Column(db.String(100), default='QA Engineering Team')
    execution_date = db.Column(db.String(50), default='2026-11-15')

    def to_dict(self):
        return {
            'id': self.id,
            'testId': self.test_id,
            'module': self.module,
            'type': self.test_type,
            'scenario': self.test_scenario,
            'preconditions': self.preconditions,
            'inputs': self.test_inputs,
            'expected': self.expected_output,
            'actual': self.actual_output,
            'result': self.test_result,
            'severity': self.severity,
            'tester': self.tester,
            'date': self.execution_date
        }

class ProjectMilestone(db.Model):
    __tablename__ = 'project_milestones'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Completed')  # Completed, In Progress, Planned
    completion_percent = db.Column(db.Integer, default=100)

    tasks = db.relationship('ProjectTask', back_populates='milestone_rel', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'startDate': self.start_date,
            'dueDate': self.due_date,
            'status': self.status,
            'completion': self.completion_percent,
            'tasksCount': len(self.tasks) if self.tasks else 0
        }

class ProjectTask(db.Model):
    __tablename__ = 'project_tasks'

    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('project_milestones.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    assignee = db.Column(db.String(100), default='Full-Stack Lead')
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    status = db.Column(db.String(50), default='Done')  # To Do, In Progress, Review, Done
    start_date = db.Column(db.String(50), default='2026-10-01')
    due_date = db.Column(db.String(50), default='2026-11-20')
    estimated_hours = db.Column(db.Float, default=8.0)
    actual_hours = db.Column(db.Float, default=7.5)

    milestone_rel = db.relationship('ProjectMilestone', back_populates='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'assignee': self.assignee,
            'priority': self.priority,
            'status': self.status,
            'startDate': self.start_date,
            'dueDate': self.due_date,
            'estimatedHours': self.estimated_hours,
            'actualHours': self.actual_hours
        }

class RiskItem(db.Model):
    __tablename__ = 'risk_items'

    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.String(20), unique=True, nullable=False)  # RSK-01
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Technical')  # Technical, Operational, Schedule, Security
    probability = db.Column(db.String(20), default='Low')  # High, Medium, Low
    impact = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    mitigation_strategy = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Mitigated')  # Open, Mitigated, Closed

    def to_dict(self):
        return {
            'id': self.id,
            'riskId': self.risk_id,
            'description': self.description,
            'category': self.category,
            'probability': self.probability,
            'impact': self.impact,
            'mitigation': self.mitigation_strategy,
            'status': self.status
        }

class PertEstimation(db.Model):
    __tablename__ = 'pert_estimations'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(150), nullable=False)
    optimistic_days = db.Column(db.Float, default=2.0)  # a
    most_likely_days = db.Column(db.Float, default=4.0)  # m
    pessimistic_days = db.Column(db.Float, default=8.0)  # b
    expected_days = db.Column(db.Float, default=4.33)  # TE = (a + 4m + b)/6
    variance = db.Column(db.Float, default=1.0)  # Var = ((b - a)/6)^2
    is_critical_path = db.Column(db.Boolean, default=True)

    def calculate(self):
        self.expected_days = round((self.optimistic_days + 4 * self.most_likely_days + self.pessimistic_days) / 6.0, 2)
        self.variance = round(((self.pessimistic_days - self.optimistic_days) / 6.0) ** 2, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'taskName': self.task_name,
            'optimistic': self.optimistic_days,
            'mostLikely': self.most_likely_days,
            'pessimistic': self.pessimistic_days,
            'expected': self.expected_days,
            'variance': self.variance,
            'criticalPath': self.is_critical_path
        }
