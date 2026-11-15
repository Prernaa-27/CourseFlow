"""
Software Engineering Lifecycle Services: SRS, MoSCoW, Architecture Diagrams, Testing QA & SPM
"""

from database import db
from models import ProjectRequirement, ArchitectureDiagram, TestCase, ProjectMilestone, ProjectTask, RiskItem, PertEstimation

def get_requirements(moscow_filter=None, category_filter=None):
    """Retrieve software requirements with optional MoSCoW filter."""
    query = ProjectRequirement.query
    if moscow_filter:
        query = query.filter_by(moscow=moscow_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    return query.order_by(ProjectRequirement.req_id).all()

def get_architecture_diagrams(diagram_type=None):
    """Retrieve system design diagrams."""
    query = ArchitectureDiagram.query
    if diagram_type:
        query = query.filter_by(diagram_type=diagram_type)
    return query.all()

def get_test_management_data():
    """Retrieve test cases and calculate QA metrics."""
    test_cases = TestCase.query.all()
    total = len(test_cases)
    passed = sum(1 for t in test_cases if t.test_result == 'Pass')
    failed = sum(1 for t in test_cases if t.test_result == 'Fail')
    blocked = sum(1 for t in test_cases if t.test_result == 'Blocked')
    not_executed = sum(1 for t in test_cases if t.test_result == 'Not Executed')
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

    return {
        'testCases': test_cases,
        'metrics': {
            'total': total,
            'passed': passed,
            'failed': failed,
            'blocked': blocked,
            'notExecuted': not_executed,
            'passRate': f"{pass_rate}%"
        }
    }

def get_spm_dashboard_data():
    """Retrieve Project Management data: milestones, tasks, risks, and PERT/CPM."""
    milestones = ProjectMilestone.query.order_by(ProjectMilestone.start_date).all()
    tasks = ProjectTask.query.all()
    risks = RiskItem.query.all()
    perts = PertEstimation.query.all()

    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t.status == 'Done')
    in_progress_tasks = sum(1 for t in tasks if t.status == 'In Progress')
    todo_tasks = sum(1 for t in tasks if t.status == 'To Do')

    # CPM Expected Duration
    critical_path_tasks = [p for p in perts if p.is_critical_path]
    cpm_total_days = round(sum(p.expected_days for p in critical_path_tasks), 1)

    return {
        'milestones': milestones,
        'tasks': tasks,
        'risks': risks,
        'perts': perts,
        'taskStats': {
            'total': total_tasks,
            'done': done_tasks,
            'inProgress': in_progress_tasks,
            'todo': todo_tasks,
            'completionRate': round((done_tasks / total_tasks) * 100, 1) if total_tasks else 0.0
        },
        'cpmTotalDays': cpm_total_days
    }
