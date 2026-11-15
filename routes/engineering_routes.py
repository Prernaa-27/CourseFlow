"""
Software Engineering Educational & Capstone Routes
Implements SRS with MoSCoW, Architecture UML/DFD Suite, Testing QA, and SPM Dashboard.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.se_service import get_requirements, get_architecture_diagrams, get_test_management_data, get_spm_dashboard_data
from services.course_service import get_course_by_id

engineering_bp = Blueprint('engineering', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@engineering_bp.route('/requirements')
@login_required
def requirements():
    user = session.get('user')
    moscow = request.args.get('moscow')
    reqs = get_requirements(moscow_filter=moscow)
    
    # Statistics
    all_reqs = get_requirements()
    counts = {
        'total': len(all_reqs),
        'must': sum(1 for r in all_reqs if r.moscow == 'Must Have'),
        'should': sum(1 for r in all_reqs if r.moscow == 'Should Have'),
        'could': sum(1 for r in all_reqs if r.moscow == 'Could Have'),
        'wont': sum(1 for r in all_reqs if r.moscow == "Won't Have")
    }
    return render_template('se_requirements.html', active_page='se_requirements', user=user, requirements=reqs, counts=counts, current_filter=moscow)

@engineering_bp.route('/architecture')
@login_required
def architecture():
    user = session.get('user')
    selected_type = request.args.get('type')
    diagrams = get_architecture_diagrams(diagram_type=selected_type)
    all_diagrams = get_architecture_diagrams()
    return render_template('se_architecture.html', active_page='se_architecture', user=user, diagrams=diagrams, all_diagrams=all_diagrams, selected_type=selected_type)

@engineering_bp.route('/testing')
@login_required
def testing():
    user = session.get('user')
    data = get_test_management_data()
    return render_template('se_testing.html', active_page='se_testing', user=user, test_cases=data['testCases'], metrics=data['metrics'])

@engineering_bp.route('/project-management')
@engineering_bp.route('/spm')
@login_required
def project_management():
    user = session.get('user')
    data = get_spm_dashboard_data()
    return render_template(
        'se_project_management.html',
        active_page='se_spm',
        user=user,
        milestones=data['milestones'],
        tasks=data['tasks'],
        risks=data['risks'],
        perts=data['perts'],
        task_stats=data['taskStats'],
        cpm_days=data['cpmTotalDays']
    )
