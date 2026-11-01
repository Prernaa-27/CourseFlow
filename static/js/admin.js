/**
 * CourseFlow - Administrator Module Controller
 * (Faculty Management, Admin Courses, Faculty Assignments, Department Monitoring)
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (document.getElementById('adminFacultyRoot')) {
    initAdminFacultyPage();
  } else if (document.getElementById('adminCoursesRoot')) {
    initAdminCoursesPage();
  } else if (document.getElementById('adminAssignmentsRoot')) {
    initAdminAssignmentsPage();
  } else if (document.getElementById('adminMonitoringRoot')) {
    initAdminMonitoringPage();
  }
});

// ==========================================================================
// 1. FACULTY MANAGEMENT
// ==========================================================================
let facultyList = [];

async function initAdminFacultyPage() {
  async function load() {
    facultyList = await CourseFlow.apiService.getFaculty();
    renderFacultyTable();
  }

  const searchInput = document.getElementById('facultySearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', () => renderFacultyTable());
  }

  const form = document.getElementById('facultyModalForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
      }

      const id = document.getElementById('facultyIdField').value;
      const name = document.getElementById('facultyNameField').value.trim();
      const email = document.getElementById('facultyEmailField').value.trim();
      const role = document.getElementById('facultyRoleField').value.trim();
      const department = document.getElementById('facultyDeptField').value;
      const experienceYears = parseInt(document.getElementById('facultyExpField').value, 10) || 5;
      const status = document.getElementById('facultyStatusField').value;

      await CourseFlow.apiService.saveFaculty({
        id: id || undefined,
        name,
        email,
        role,
        department,
        experienceYears,
        status,
        assignedCourses: id ? (facultyList.find(f => f.id === id)?.assignedCourses || []) : []
      });

      CourseFlow.showToast(`Faculty member "${name}" saved`, 'success');
      const modal = bootstrap.Modal.getInstance(document.getElementById('facultyModal'));
      if (modal) modal.hide();
      await load();
    });
  }

  await load();
}

function renderFacultyTable() {
  const tbody = document.getElementById('facultyTableTbody');
  if (!tbody) return;

  const search = (document.getElementById('facultySearchInput')?.value || '').toLowerCase().trim();
  const filtered = facultyList.filter(f => !search || f.name.toLowerCase().includes(search) || f.email.toLowerCase().includes(search) || f.department.toLowerCase().includes(search));

  if (document.getElementById('facultyTotalBadge')) {
    document.getElementById('facultyTotalBadge').textContent = `${filtered.length} Faculty Members`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No faculty members found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(f => `
    <tr>
      <td class="fw-bold text-dark">${f.id}</td>
      <td>
        <div class="fw-semibold text-dark">${f.name}</div>
        <div class="text-muted small" style="font-size:0.75rem;">${f.email}</div>
      </td>
      <td class="small text-secondary">${f.role}</td>
      <td class="small text-muted">${f.department}</td>
      <td class="small text-center">
        <span class="badge bg-light text-dark border">${f.assignedCourses ? f.assignedCourses.length : 0} Courses</span>
      </td>
      <td>
        <span class="badge ${f.status === 'Active' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary text-white'}">
          ${f.status}
        </span>
      </td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-secondary py-1 px-2" onclick="openFacultyModal('${f.id}')"><i class="bi bi-pencil"></i></button>
      </td>
    </tr>
  `).join('');
}

window.openFacultyModal = function(facId) {
  const form = document.getElementById('facultyModalForm');
  form.classList.remove('was-validated');

  const f = facId ? facultyList.find(item => item.id === facId) : null;
  document.getElementById('facultyIdField').value = f ? f.id : '';
  document.getElementById('facultyNameField').value = f ? f.name : '';
  document.getElementById('facultyEmailField').value = f ? f.email : '';
  document.getElementById('facultyRoleField').value = f ? f.role : 'Assistant Professor';
  document.getElementById('facultyDeptField').value = f ? f.department : 'Computer Science & Engineering';
  document.getElementById('facultyExpField').value = f ? f.experienceYears : 5;
  document.getElementById('facultyStatusField').value = f ? f.status : 'Active';
  document.getElementById('facultyModalTitle').textContent = f ? `Edit Faculty: ${f.name}` : 'Add Faculty Member';

  const modal = new bootstrap.Modal(document.getElementById('facultyModal'));
  modal.show();
};

// ==========================================================================
// 2. ADMIN COURSE MANAGEMENT
// ==========================================================================
async function initAdminCoursesPage() {
  const courses = await CourseFlow.apiService.getCourses();
  const tbody = document.getElementById('adminCoursesTableTbody');
  if (tbody) {
    tbody.innerHTML = courses.map(c => `
      <tr>
        <td class="fw-bold text-dark">${c.code}</td>
        <td>${c.title}</td>
        <td class="small text-muted">${c.semester}</td>
        <td class="small text-muted">${c.academicYear}</td>
        <td class="small text-dark">${c.faculty}</td>
        <td>${CourseFlow.renderStatusBadge(c.status)}</td>
        <td class="text-end">
          <a href="/courses/${c.id}" class="btn btn-sm btn-outline-primary py-1 px-2"><i class="bi bi-eye"></i></a>
        </td>
      </tr>
    `).join('');
  }
}

// ==========================================================================
// 3. FACULTY-COURSE ASSIGNMENTS
// ==========================================================================
async function initAdminAssignmentsPage() {
  const courses = await CourseFlow.apiService.getCourses();
  const faculty = await CourseFlow.apiService.getFaculty();

  const tbody = document.getElementById('assignmentsTableTbody');
  if (!tbody) return;

  function renderTable() {
    tbody.innerHTML = courses.map(c => `
      <tr>
        <td>
          <div class="fw-bold text-dark">${c.code}</div>
          <div class="text-secondary small" style="font-size:0.75rem;">${c.title}</div>
        </td>
        <td class="small text-muted">${c.semester} &bull; ${c.academicYear}</td>
        <td>
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-person-circle text-primary"></i>
            <span class="fw-semibold text-dark">${c.faculty}</span>
          </div>
        </td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-primary py-1 px-2" onclick="openAssignModal('${c.id}')">
            <i class="bi bi-arrow-left-right me-1"></i> Change Assignment
          </button>
        </td>
      </tr>
    `).join('');
  }

  // Assign Modal
  window.openAssignModal = function(courseId) {
    const c = courses.find(item => item.id === courseId);
    if (!c) return;

    document.getElementById('assignCourseId').value = c.id;
    document.getElementById('assignCourseLabel').textContent = `${c.code} - ${c.title}`;
    
    const select = document.getElementById('assignFacultySelect');
    select.innerHTML = faculty.filter(f => f.status === 'Active').map(f => `
      <option value="${f.name}" ${f.name === c.faculty ? 'selected' : ''}>${f.name} (${f.department})</option>
    `).join('');

    const modal = new bootstrap.Modal(document.getElementById('assignModal'));
    modal.show();
  };

  const assignForm = document.getElementById('assignModalForm');
  if (assignForm) {
    assignForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const courseId = document.getElementById('assignCourseId').value;
      const newFaculty = document.getElementById('assignFacultySelect').value;

      const course = courses.find(c => c.id === courseId);
      if (course) {
        course.faculty = newFaculty;
        await CourseFlow.apiService.saveCourse(course);
        CourseFlow.showToast(`Faculty assignment updated for ${course.code}`, 'success');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('assignModal'));
        if (modal) modal.hide();
        renderTable();
      }
    });
  }

  renderTable();
}

// ==========================================================================
// 4. DEPARTMENT COMPLETION MONITORING
// ==========================================================================
async function initAdminMonitoringPage() {
  const courses = await CourseFlow.apiService.getCourses();

  // Statistics
  const totalCourses = courses.length;
  const completedCourses = courses.filter(c => c.completion === 100).length;
  const inProgressCourses = courses.filter(c => c.completion >= 50 && c.completion < 100).length;
  const laggingCourses = courses.filter(c => c.completion < 50).length;
  const avgCompletion = Math.round(courses.reduce((acc, c) => acc + c.completion, 0) / totalCourses);

  if (document.getElementById('monAvgCompletion')) document.getElementById('monAvgCompletion').textContent = `${avgCompletion}%`;
  if (document.getElementById('monCompletedCount')) document.getElementById('monCompletedCount').textContent = completedCourses;
  if (document.getElementById('monInProgressCount')) document.getElementById('monInProgressCount').textContent = inProgressCourses;
  if (document.getElementById('monLaggingCount')) document.getElementById('monLaggingCount').textContent = laggingCourses;

  // Chart
  const ctx = document.getElementById('departmentProgressChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Completed (100%)', 'In Progress (50-99%)', 'Needs Attention (<50%)'],
        datasets: [{
          data: [completedCourses, inProgressCourses, laggingCourses],
          backgroundColor: ['#16A34A', '#4338CA', '#F59E0B']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } } }
        }
      }
    });
  }

  // Monitoring table
  const tbody = document.getElementById('monitoringTableTbody');
  if (tbody) {
    tbody.innerHTML = courses.map(c => `
      <tr>
        <td class="fw-bold text-dark">${c.code}</td>
        <td>${c.title}</td>
        <td class="small text-muted">${c.faculty}</td>
        <td class="small text-muted">${c.semester}</td>
        <td style="min-width: 140px;">
          <div class="d-flex justify-content-between small mb-1">
            <span class="fw-semibold">${c.completion}%</span>
          </div>
          <div class="cf-progress">
            <div class="cf-progress-bar ${c.completion === 100 ? 'cf-progress-bar-success' : c.completion < 50 ? 'cf-progress-bar-warning' : 'cf-progress-bar-indigo'}" 
                 style="width: ${c.completion}%"></div>
          </div>
        </td>
        <td>${CourseFlow.renderStatusBadge(c.status)}</td>
        <td class="text-end">
          <a href="/course-file?course_id=${c.id}" class="btn btn-sm btn-outline-primary py-1 px-2" style="font-size:0.75rem;">Audit Handout</a>
        </td>
      </tr>
    `).join('');
  }

  // Export report
  const exportBtn = document.getElementById('exportMonitoringReportBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      CourseFlow.showToast('Department Course File Compliance Report (CSV) exported for Dean review.', 'success', 'Report Exported');
    });
  }
}
