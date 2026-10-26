/**
 * CourseFlow - Academic Records Controller (Simplified)
 * (Syllabus, Session Planner, Students, Assessments, Marks, Attendance, Feedback)
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (document.getElementById('syllabusRoot')) {
    initSyllabusPage();
  } else if (document.getElementById('sessionPlannerRoot')) {
    initSessionPlannerPage();
  } else if (document.getElementById('studentsRoot')) {
    initStudentsPage();
  } else if (document.getElementById('assessmentsRoot')) {
    initAssessmentsPage();
  } else if (document.getElementById('marksRoot')) {
    initMarksPage();
  } else if (document.getElementById('attendanceRoot')) {
    initAttendancePage();
  } else if (document.getElementById('feedbackRoot')) {
    initFeedbackPage();
  }
});

// ==========================================================================
// 1. SYLLABUS MANAGEMENT
// ==========================================================================
async function initSyllabusPage() {
  const courseSelect = document.getElementById('syllabusCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function loadUnits() {
    const units = await CourseFlow.apiService.getSyllabus(currentCourse);
    renderSyllabusUnits(units);
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      loadUnits();
    });
  }

  const addBtn = document.getElementById('addUnitBtn');
  if (addBtn) {
    addBtn.addEventListener('click', () => {
      openUnitModal(null);
    });
  }

  const reviewBtn = document.getElementById('markReviewedBtn');
  if (reviewBtn) {
    reviewBtn.addEventListener('click', () => {
      CourseFlow.showToast('Syllabus marked as reviewed.', 'success', 'Syllabus Reviewed');
    });
  }

  const uploadInput = document.getElementById('syllabusFileInput');
  if (uploadInput) {
    uploadInput.addEventListener('change', () => {
      CourseFlow.showToast('Demo import: File selected. Modules loaded into view.', 'info', 'File Loaded');
    });
  }

  await loadUnits();
}

function renderSyllabusUnits(units) {
  const container = document.getElementById('syllabusUnitsContainer');
  const totalHoursEl = document.getElementById('totalTeachingHours');
  if (!container) return;

  const totalHours = units.reduce((acc, u) => acc + (parseInt(u.hours, 10) || 0), 0);
  if (totalHoursEl) totalHoursEl.textContent = `${totalHours} Hours`;

  if (units.length === 0) {
    container.innerHTML = `<div class="p-4 text-center text-muted">No units defined for this course yet. Click "Add Unit" to start.</div>`;
    return;
  }

  container.innerHTML = units.map(u => `
    <div class="cf-card mb-3 p-3">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <span class="badge bg-primary-subtle text-primary fw-bold me-2">Unit ${u.unit}</span>
          <strong class="text-dark fs-6">${u.title}</strong>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-secondary py-1 px-2" onclick="editUnit(${u.unit})"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger py-1 px-2" onclick="deleteUnit(${u.unit})"><i class="bi bi-trash"></i></button>
        </div>
      </div>
      <p class="text-secondary small mb-2">${u.topics}</p>
      <div class="d-flex gap-3 small text-muted pt-2 border-top">
        <span><i class="bi bi-clock me-1 text-primary"></i><strong>${u.hours}</strong> Teaching Hours</span>
        <span><i class="bi bi-check-circle me-1 text-success"></i>Outcomes: <strong>${u.outcomes}</strong></span>
      </div>
    </div>
  `).join('');
}

window.openUnitModal = async function(unitNumber) {
  const courseSelect = document.getElementById('syllabusCourseSelect');
  const courseId = courseSelect ? courseSelect.value : 'CS301';
  const units = await CourseFlow.apiService.getSyllabus(courseId);

  const unit = unitNumber ? units.find(u => u.unit === unitNumber) : null;
  document.getElementById('unitModalNumber').value = unit ? unit.unit : (units.length + 1);
  document.getElementById('unitModalTitle').value = unit ? unit.title : '';
  document.getElementById('unitModalHours').value = unit ? unit.hours : 8;
  document.getElementById('unitModalOutcomes').value = unit ? unit.outcomes : 'CO1';
  document.getElementById('unitModalTopics').value = unit ? unit.topics : '';

  const modal = new bootstrap.Modal(document.getElementById('unitModal'));
  modal.show();
};

window.saveUnitFromModal = async function() {
  const form = document.getElementById('unitModalForm');
  if (!form.checkValidity()) {
    form.classList.add('was-validated');
    return;
  }

  const courseSelect = document.getElementById('syllabusCourseSelect');
  const courseId = courseSelect ? courseSelect.value : 'CS301';
  const units = await CourseFlow.apiService.getSyllabus(courseId);

  const unitNo = parseInt(document.getElementById('unitModalNumber').value, 10);
  const title = document.getElementById('unitModalTitle').value.trim();
  const hours = parseInt(document.getElementById('unitModalHours').value, 10);
  const outcomes = document.getElementById('unitModalOutcomes').value.trim();
  const topics = document.getElementById('unitModalTopics').value.trim();

  const idx = units.findIndex(u => u.unit === unitNo);
  const updated = { unit: unitNo, title, hours, outcomes, topics };
  if (idx >= 0) {
    units[idx] = updated;
  } else {
    units.push(updated);
  }

  units.sort((a, b) => a.unit - b.unit);
  await CourseFlow.apiService.saveSyllabus(courseId, units);
  CourseFlow.showToast(`Unit ${unitNo} saved successfully`, 'success');

  const modal = bootstrap.Modal.getInstance(document.getElementById('unitModal'));
  if (modal) modal.hide();

  renderSyllabusUnits(units);
};

window.editUnit = function(unitNo) {
  openUnitModal(unitNo);
};

window.deleteUnit = async function(unitNo) {
  CourseFlow.confirmAction(
    `Are you sure you want to delete Unit ${unitNo}?`,
    async () => {
      const courseSelect = document.getElementById('syllabusCourseSelect');
      const courseId = courseSelect ? courseSelect.value : 'CS301';
      let units = await CourseFlow.apiService.getSyllabus(courseId);
      units = units.filter(u => u.unit !== unitNo);
      await CourseFlow.apiService.saveSyllabus(courseId, units);
      CourseFlow.showToast(`Unit ${unitNo} removed`, 'info');
      renderSyllabusUnits(units);
    },
    'Delete Unit'
  );
};

// ==========================================================================
// 2. SESSION PLANNER
// ==========================================================================
let currentSessions = [];

async function initSessionPlannerPage() {
  const courseSelect = document.getElementById('sessionCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function loadSessions() {
    currentSessions = await CourseFlow.apiService.getSessionPlans(currentCourse);
    renderSessions();
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      loadSessions();
    });
  }

  const searchInput = document.getElementById('sessionSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', () => renderSessions());
  }

  const statusFilter = document.getElementById('sessionStatusFilter');
  if (statusFilter) {
    statusFilter.addEventListener('change', () => renderSessions());
  }

  await loadSessions();
}

function renderSessions() {
  const container = document.getElementById('sessionTableTbody');
  const summaryEl = document.getElementById('sessionSummaryText');
  if (!container) return;

  const search = (document.getElementById('sessionSearchInput')?.value || '').toLowerCase().trim();
  const status = document.getElementById('sessionStatusFilter')?.value || '';

  const filtered = currentSessions.filter(s => {
    const matchSearch = !search || s.topic.toLowerCase().includes(search) || s.lo.toLowerCase().includes(search);
    const matchStatus = !status || s.status === status;
    return matchSearch && matchStatus;
  });

  const total = currentSessions.length;
  const completed = currentSessions.filter(s => s.status === 'Completed').length;
  if (summaryEl) {
    summaryEl.textContent = `${completed} of ${total} sessions conducted (${total > 0 ? Math.round((completed/total)*100) : 0}%)`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No sessions match the selected filter.</td></tr>`;
    return;
  }

  container.innerHTML = filtered.map(s => `
    <tr>
      <td class="fw-bold text-center">#${s.sessionNo}</td>
      <td>
        <div class="fw-semibold text-dark">${s.topic}</div>
        <div class="text-muted small" style="font-size:0.75rem;"><i class="bi bi-book me-1"></i>${s.resources}</div>
      </td>
      <td class="small text-center"><span class="badge bg-light text-dark border">${s.lo}</span></td>
      <td class="small text-muted">${s.date}</td>
      <td class="small text-muted">${s.duration}</td>
      <td class="small text-secondary">${s.method}</td>
      <td>
        <span class="badge ${s.status === 'Completed' ? 'bg-success-subtle text-success border border-success-subtle' : s.status === 'Rescheduled' ? 'bg-danger-subtle text-danger border' : 'bg-warning-subtle text-warning border border-warning-subtle'}">
          ${s.status}
        </span>
      </td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-secondary py-1 px-2" onclick="openSessionModal('${s.id}')"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-outline-danger py-1 px-2" onclick="deleteSessionPlan('${s.id}')"><i class="bi bi-trash"></i></button>
      </td>
    </tr>
  `).join('');
}

window.openSessionModal = function(sessionId) {
  const s = sessionId ? currentSessions.find(item => item.id === sessionId) : null;
  document.getElementById('sessionIdField').value = s ? s.id : '';
  document.getElementById('sessionNoField').value = s ? s.sessionNo : (currentSessions.length + 1);
  document.getElementById('sessionTopicField').value = s ? s.topic : '';
  document.getElementById('sessionLOField').value = s ? s.lo : 'CO1';
  document.getElementById('sessionDateField').value = s ? s.date : new Date().toISOString().split('T')[0];
  document.getElementById('sessionDurationField').value = s ? s.duration : '60 min';
  document.getElementById('sessionMethodField').value = s ? s.method : 'Interactive Lecture';
  document.getElementById('sessionResourcesField').value = s ? s.resources : 'Lecture Slides';
  document.getElementById('sessionStatusField').value = s ? s.status : 'Planned';

  const modal = new bootstrap.Modal(document.getElementById('sessionModal'));
  modal.show();
};

window.saveSessionPlanModal = async function() {
  const form = document.getElementById('sessionModalForm');
  if (!form.checkValidity()) {
    form.classList.add('was-validated');
    return;
  }

  const courseSelect = document.getElementById('sessionCourseSelect');
  const courseId = courseSelect ? courseSelect.value : 'CS301';

  const id = document.getElementById('sessionIdField').value;
  const session = {
    id: id || 'S' + (currentSessions.length + 1).toString().padStart(2, '0'),
    sessionNo: parseInt(document.getElementById('sessionNoField').value, 10),
    topic: document.getElementById('sessionTopicField').value.trim(),
    lo: document.getElementById('sessionLOField').value.trim(),
    date: document.getElementById('sessionDateField').value,
    duration: document.getElementById('sessionDurationField').value.trim(),
    method: document.getElementById('sessionMethodField').value.trim(),
    resources: document.getElementById('sessionResourcesField').value.trim(),
    status: document.getElementById('sessionStatusField').value
  };

  await CourseFlow.apiService.saveSessionPlan(courseId, session);
  CourseFlow.showToast(`Session #${session.sessionNo} saved`, 'success');

  const modal = bootstrap.Modal.getInstance(document.getElementById('sessionModal'));
  if (modal) modal.hide();

  currentSessions = await CourseFlow.apiService.getSessionPlans(courseId);
  renderSessions();
};

window.deleteSessionPlan = function(sessionId) {
  CourseFlow.confirmAction('Delete this session plan record?', async () => {
    const courseSelect = document.getElementById('sessionCourseSelect');
    const courseId = courseSelect ? courseSelect.value : 'CS301';
    await CourseFlow.apiService.deleteSessionPlan(courseId, sessionId);
    currentSessions = await CourseFlow.apiService.getSessionPlans(courseId);
    renderSessions();
    CourseFlow.showToast('Session deleted', 'info');
  });
};

// ==========================================================================
// 3. STUDENT MANAGEMENT
// ==========================================================================
let allStudentsList = [];

async function initStudentsPage() {
  const courseFilter = document.getElementById('studentCourseFilter');
  const searchInput = document.getElementById('studentSearchInput');

  async function load() {
    allStudentsList = await CourseFlow.apiService.getStudents();
    renderStudents();
  }

  if (courseFilter) {
    courseFilter.addEventListener('change', () => renderStudents());
  }
  if (searchInput) {
    searchInput.addEventListener('input', () => renderStudents());
  }

  const studentForm = document.getElementById('studentModalForm');
  if (studentForm) {
    studentForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!studentForm.checkValidity()) {
        studentForm.classList.add('was-validated');
        return;
      }

      const id = document.getElementById('studentIdField').value.trim().toUpperCase();
      const name = document.getElementById('studentNameField').value.trim();
      const email = document.getElementById('studentEmailField').value.trim();
      const courseId = document.getElementById('studentCourseField').value;
      const section = document.getElementById('studentSectionField').value;

      await CourseFlow.apiService.saveStudent({ id, name, email, courseId, section, status: 'Enrolled' });
      CourseFlow.showToast(`Student ${name} saved`, 'success');

      const modal = bootstrap.Modal.getInstance(document.getElementById('studentModal'));
      if (modal) modal.hide();

      await load();
    });
  }

  await load();
}

function renderStudents() {
  const tbody = document.getElementById('studentsTableTbody');
  if (!tbody) return;

  const search = (document.getElementById('studentSearchInput')?.value || '').toLowerCase().trim();
  const courseFilter = document.getElementById('studentCourseFilter')?.value || '';

  const filtered = allStudentsList.filter(s => {
    const matchSearch = !search || s.name.toLowerCase().includes(search) || s.id.toLowerCase().includes(search) || s.email.toLowerCase().includes(search);
    const matchCourse = !courseFilter || s.courseId === courseFilter;
    return matchSearch && matchCourse;
  });

  const countBadge = document.getElementById('studentsTotalBadge');
  if (countBadge) countBadge.textContent = `${filtered.length} Students`;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No student records found matching search.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(s => `
    <tr>
      <td class="fw-bold text-dark">${s.id}</td>
      <td>
        <div class="fw-semibold text-dark">${s.name}</div>
        <div class="text-muted small" style="font-size:0.75rem;">${s.email}</div>
      </td>
      <td class="small text-secondary"><span class="badge bg-light text-dark border">${s.courseId}</span></td>
      <td class="small text-center">${s.section}</td>
      <td><span class="badge bg-success-subtle text-success border border-success-subtle">Enrolled</span></td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-secondary py-1 px-2" onclick="openStudentModal('${s.id}')"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-outline-danger py-1 px-2" onclick="deleteStudent('${s.id}')"><i class="bi bi-trash"></i></button>
      </td>
    </tr>
  `).join('');
}

window.openStudentModal = function(studentId) {
  const form = document.getElementById('studentModalForm');
  form.classList.remove('was-validated');

  const s = studentId ? allStudentsList.find(i => i.id === studentId) : null;
  const idField = document.getElementById('studentIdField');
  idField.value = s ? s.id : '';
  idField.disabled = !!s;

  document.getElementById('studentNameField').value = s ? s.name : '';
  document.getElementById('studentEmailField').value = s ? s.email : '';
  document.getElementById('studentCourseField').value = s ? s.courseId : 'CS301';
  document.getElementById('studentSectionField').value = s ? s.section : 'A';
  document.getElementById('studentModalTitle').textContent = s ? `Edit Student: ${s.id}` : 'Enroll New Student';

  const modal = new bootstrap.Modal(document.getElementById('studentModal'));
  modal.show();
};

window.deleteStudent = function(studentId) {
  CourseFlow.confirmAction(`Remove student ${studentId}?`, async () => {
    await CourseFlow.apiService.deleteStudent(studentId);
    allStudentsList = await CourseFlow.apiService.getStudents();
    renderStudents();
    CourseFlow.showToast(`Student ${studentId} removed`, 'info');
  });
};

// ==========================================================================
// 4. ASSESSMENTS
// ==========================================================================
let allAssessments = [];

async function initAssessmentsPage() {
  const courseFilter = document.getElementById('assessmentCourseFilter');
  let currentCourse = courseFilter ? courseFilter.value : 'CS301';

  async function load() {
    allAssessments = await CourseFlow.apiService.getAssessments(currentCourse);
    renderAssessments();
  }

  if (courseFilter) {
    courseFilter.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      load();
    });
  }

  const asmForm = document.getElementById('assessmentModalForm');
  if (asmForm) {
    asmForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!asmForm.checkValidity()) {
        asmForm.classList.add('was-validated');
        return;
      }

      const id = document.getElementById('assessmentIdField').value;
      const title = document.getElementById('assessmentTitleField').value.trim();
      const type = document.getElementById('assessmentTypeField').value;
      const courseId = document.getElementById('assessmentCourseField').value;
      const maxMarks = parseInt(document.getElementById('assessmentMaxMarksField').value, 10);
      const weightage = parseInt(document.getElementById('assessmentWeightageField').value, 10);
      const date = document.getElementById('assessmentDateField').value;
      const co = document.getElementById('assessmentCOField').value.trim();
      const status = document.getElementById('assessmentStatusField').value;

      await CourseFlow.apiService.saveAssessment({ id, title, type, courseId, maxMarks, weightage, date, co, status });
      CourseFlow.showToast(`Assessment "${title}" saved`, 'success');

      const modal = bootstrap.Modal.getInstance(document.getElementById('assessmentModal'));
      if (modal) modal.hide();

      await load();
    });
  }

  await load();
}

function renderAssessments() {
  const tbody = document.getElementById('assessmentsTableTbody');
  if (!tbody) return;

  if (allAssessments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No assessments configured for this course yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = allAssessments.map(a => `
    <tr>
      <td>
        <div class="fw-semibold text-dark">${a.title}</div>
        <div class="text-muted small" style="font-size:0.75rem;"><i class="bi bi-tag me-1"></i>${a.type}</div>
      </td>
      <td class="small text-muted">${a.courseId}</td>
      <td class="small text-center fw-bold">${a.maxMarks}</td>
      <td class="small text-center">${a.weightage}%</td>
      <td class="small text-muted">${a.date}</td>
      <td class="small text-center"><span class="badge bg-light text-dark border">${a.co}</span></td>
      <td>
        <span class="badge ${a.status === 'Graded' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'}">
          ${a.status}
        </span>
      </td>
      <td class="text-end">
        <a href="/marks?assessment=${a.id}" class="btn btn-sm btn-outline-primary py-1 px-2" title="Enter Marks"><i class="bi bi-pencil-square"></i> Marks</a>
        <button class="btn btn-sm btn-outline-secondary py-1 px-2" onclick="openAssessmentModal('${a.id}')"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-outline-danger py-1 px-2" onclick="deleteAssessment('${a.id}')"><i class="bi bi-trash"></i></button>
      </td>
    </tr>
  `).join('');
}

window.openAssessmentModal = function(asmId) {
  const form = document.getElementById('assessmentModalForm');
  form.classList.remove('was-validated');

  const a = asmId ? allAssessments.find(i => i.id === asmId) : null;
  document.getElementById('assessmentIdField').value = a ? a.id : '';
  document.getElementById('assessmentTitleField').value = a ? a.title : '';
  document.getElementById('assessmentTypeField').value = a ? a.type : 'Internal Exam';
  document.getElementById('assessmentCourseField').value = a ? a.courseId : 'CS301';
  document.getElementById('assessmentMaxMarksField').value = a ? a.maxMarks : 50;
  document.getElementById('assessmentWeightageField').value = a ? a.weightage : 20;
  document.getElementById('assessmentDateField').value = a ? a.date : new Date().toISOString().split('T')[0];
  document.getElementById('assessmentCOField').value = a ? a.co : 'CO1, CO2';
  document.getElementById('assessmentStatusField').value = a ? a.status : 'Pending';

  const modal = new bootstrap.Modal(document.getElementById('assessmentModal'));
  modal.show();
};

window.deleteAssessment = function(asmId) {
  CourseFlow.confirmAction('Delete this assessment and associated marks?', async () => {
    await CourseFlow.apiService.deleteAssessment(asmId);
    const courseFilter = document.getElementById('assessmentCourseFilter');
    allAssessments = await CourseFlow.apiService.getAssessments(courseFilter ? courseFilter.value : 'CS301');
    renderAssessments();
    CourseFlow.showToast('Assessment deleted', 'info');
  });
};

// ==========================================================================
// 5. MARKS ENTRY
// ==========================================================================
let currentMarksMap = {};
let currentSelectedAssessment = null;

async function initMarksPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const paramAsm = urlParams.get('assessment') || 'ASM01';

  const asmSelect = document.getElementById('marksAssessmentSelect');

  async function loadMarks() {
    const asmId = asmSelect ? asmSelect.value : paramAsm;
    const allAsms = await CourseFlow.apiService.getAssessments();
    currentSelectedAssessment = allAsms.find(a => a.id === asmId) || allAsms[0];
    currentMarksMap = await CourseFlow.apiService.getMarks(asmId);
    
    if (document.getElementById('marksMaxBadge')) {
      document.getElementById('marksMaxBadge').textContent = `Max Marks: ${currentSelectedAssessment.maxMarks}`;
    }
    renderMarksEntryTable();
  }

  if (asmSelect) {
    asmSelect.value = paramAsm;
    asmSelect.addEventListener('change', () => loadMarks());
  }

  const saveBtn = document.getElementById('saveMarksBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const inputs = document.querySelectorAll('.student-mark-input');
      let hasError = false;
      const updatedMap = {};

      inputs.forEach(input => {
        const studentId = input.dataset.studentId;
        const val = input.value.trim();
        if (val !== '') {
          const num = parseFloat(val);
          if (isNaN(num) || num < 0 || num > currentSelectedAssessment.maxMarks) {
            input.classList.add('is-invalid');
            hasError = true;
          } else {
            input.classList.remove('is-invalid');
            updatedMap[studentId] = num;
          }
        }
      });

      if (hasError) {
        CourseFlow.showToast(`Some marks exceed maximum (${currentSelectedAssessment.maxMarks}) or are negative.`, 'danger', 'Validation Error');
        return;
      }

      await CourseFlow.apiService.saveMarks(currentSelectedAssessment.id, updatedMap);
      CourseFlow.showToast('Marks saved successfully!', 'success', 'Saved');
      await loadMarks();
    });
  }

  await loadMarks();
}

async function renderMarksEntryTable() {
  const tbody = document.getElementById('marksTableTbody');
  if (!tbody || !currentSelectedAssessment) return;

  const students = await CourseFlow.apiService.getStudents(currentSelectedAssessment.courseId);
  const max = currentSelectedAssessment.maxMarks;

  let totalEntered = 0;
  let sumEntered = 0;

  tbody.innerHTML = students.map(s => {
    const val = currentMarksMap[s.id] !== undefined ? currentMarksMap[s.id] : '';
    if (val !== '') {
      totalEntered++;
      sumEntered += parseFloat(val);
    }
    const pct = val !== '' ? Math.round((val / max) * 100) : '-';

    return `
      <tr>
        <td class="fw-bold">${s.id}</td>
        <td>${s.name}</td>
        <td class="text-center text-muted">${s.section}</td>
        <td style="max-width: 140px;">
          <input type="number" 
                 class="form-control form-control-sm text-center fw-bold student-mark-input ${val === '' ? 'border-warning' : ''}" 
                 data-student-id="${s.id}" 
                 value="${val}" 
                 min="0" 
                 max="${max}" 
                 step="0.5" 
                 placeholder="Pending">
        </td>
        <td class="text-center fw-semibold text-secondary">${pct !== '-' ? pct + '%' : '<span class="text-warning small">Missing</span>'}</td>
      </tr>
    `;
  }).join('');

  if (document.getElementById('marksSummaryEntered')) {
    document.getElementById('marksSummaryEntered').textContent = `${totalEntered} / ${students.length}`;
  }
  if (document.getElementById('marksSummaryAverage')) {
    const avg = totalEntered > 0 ? (sumEntered / totalEntered).toFixed(1) : 0;
    document.getElementById('marksSummaryAverage').textContent = `${avg} / ${max}`;
  }
}

// ==========================================================================
// 6. ATTENDANCE MANAGEMENT (Present / Absent Only)
// ==========================================================================
let currentAttendanceData = null;

async function initAttendancePage() {
  const courseSelect = document.getElementById('attendanceCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function load() {
    currentAttendanceData = await CourseFlow.apiService.getAttendance(currentCourse);
    renderAttendanceInterface();
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      load();
    });
  }

  // Bulk actions: P or A
  const markAllPresentBtn = document.getElementById('markAllPresentBtn');
  if (markAllPresentBtn) {
    markAllPresentBtn.addEventListener('click', () => {
      document.querySelectorAll('.attendance-radio[value="P"]').forEach(r => r.checked = true);
      CourseFlow.showToast('All students marked Present for this session', 'info');
    });
  }

  const markAllAbsentBtn = document.getElementById('markAllAbsentBtn');
  if (markAllAbsentBtn) {
    markAllAbsentBtn.addEventListener('click', () => {
      document.querySelectorAll('.attendance-radio[value="A"]').forEach(r => r.checked = true);
      CourseFlow.showToast('All students marked Absent for this session', 'info');
    });
  }

  // Save attendance
  const saveBtn = document.getElementById('saveAttendanceBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const dateSelect = document.getElementById('attendanceDateSelect');
      const selectedDateIndex = parseInt(dateSelect.value, 10);
      
      const students = await CourseFlow.apiService.getStudents(currentCourse);
      students.forEach(s => {
        const checked = document.querySelector(`.attendance-radio[name="att_${s.id}"]:checked`);
        if (checked && currentAttendanceData.records[s.id]) {
          currentAttendanceData.records[s.id][selectedDateIndex] = checked.value;
        }
      });

      await CourseFlow.apiService.saveAttendance(currentCourse, currentAttendanceData);
      CourseFlow.showToast('Attendance records saved successfully!', 'success');
      renderAttendanceInterface();
    });
  }

  await load();
}

async function renderAttendanceInterface() {
  const tbody = document.getElementById('attendanceTableTbody');
  if (!tbody || !currentAttendanceData) return;

  const dateSelect = document.getElementById('attendanceDateSelect');
  const dateIndex = dateSelect ? parseInt(dateSelect.value, 10) : 0;
  const courseSelect = document.getElementById('attendanceCourseSelect');
  const courseId = courseSelect ? courseSelect.value : 'CS301';

  const students = await CourseFlow.apiService.getStudents(courseId);
  const totalSessions = currentAttendanceData.dates.length;

  let belowThresholdCount = 0;

  tbody.innerHTML = students.map(s => {
    const list = currentAttendanceData.records[s.id] || [];
    const currentStatus = list[dateIndex] || 'P';
    
    // Percentage = (Present count / total sessions) * 100
    const presentCount = list.filter(status => status === 'P').length;
    const pct = totalSessions > 0 ? Math.round((presentCount / totalSessions) * 100) : 100;
    
    if (pct < 75) belowThresholdCount++;

    return `
      <tr>
        <td class="fw-bold text-dark">${s.id}</td>
        <td>${s.name}</td>
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <input type="radio" class="btn-check attendance-radio" name="att_${s.id}" id="p_${s.id}" value="P" ${currentStatus === 'P' ? 'checked' : ''}>
            <label class="btn btn-outline-success py-1 px-3" for="p_${s.id}">Present</label>

            <input type="radio" class="btn-check attendance-radio" name="att_${s.id}" id="a_${s.id}" value="A" ${currentStatus === 'A' ? 'checked' : ''}>
            <label class="btn btn-outline-danger py-1 px-3" for="a_${s.id}">Absent</label>
          </div>
        </td>
        <td class="text-center fw-semibold ${pct < 75 ? 'text-danger' : 'text-dark'}">
          ${pct}% ${pct < 75 ? '<i class="bi bi-exclamation-triangle-fill text-danger ms-1" title="Below 75% attendance"></i>' : ''}
        </td>
      </tr>
    `;
  }).join('');

  if (document.getElementById('lowAttendanceAlertBadge')) {
    document.getElementById('lowAttendanceAlertBadge').textContent = `${belowThresholdCount} Students Below 75%`;
  }
}

// ==========================================================================
// 7. FEEDBACK MANAGEMENT (Interactive Rating & Comments)
// ==========================================================================
let feedbackChartInstance = null;

async function initFeedbackPage() {
  const courseSelect = document.getElementById('feedbackCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function load() {
    const data = await CourseFlow.apiService.getFeedback(currentCourse);
    renderFeedbackView(data);
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      load();
    });
  }

  // Interactive Feedback Submission Form
  const feedbackForm = document.getElementById('submitFeedbackForm');
  if (feedbackForm) {
    feedbackForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const rating = document.getElementById('feedbackRatingInput').value;
      const commentInput = document.getElementById('feedbackCommentInput');
      const comment = commentInput ? commentInput.value.trim() : '';

      await CourseFlow.apiService.addFeedback(currentCourse, rating, comment);
      CourseFlow.showToast(`Feedback of ${rating} stars recorded!`, 'success', 'Feedback Submitted');
      if (commentInput) commentInput.value = '';
      await load();
    });
  }

  await load();
}

function renderFeedbackView(data) {
  if (!data) return;

  if (document.getElementById('feedbackAvgScore')) {
    document.getElementById('feedbackAvgScore').textContent = data.averageRating.toFixed(1);
  }
  if (document.getElementById('feedbackTotalResponses')) {
    document.getElementById('feedbackTotalResponses').textContent = `${data.totalResponses} Responses`;
  }

  // Category ratings
  const catContainer = document.getElementById('feedbackCategoriesList');
  if (catContainer) {
    catContainer.innerHTML = (data.categories || []).map(c => `
      <div class="mb-3">
        <div class="d-flex justify-content-between small fw-semibold mb-1">
          <span>${c.name}</span>
          <span class="text-primary">${c.rating} / ${c.outOf}</span>
        </div>
        <div class="cf-progress">
          <div class="cf-progress-bar cf-progress-bar-indigo" style="width: ${(c.rating / c.outOf) * 100}%"></div>
        </div>
      </div>
    `).join('');
  }

  // Comments List
  const commentsContainer = document.getElementById('feedbackCommentsList');
  if (commentsContainer) {
    if (!data.comments || data.comments.length === 0) {
      commentsContainer.innerHTML = `<div class="p-3 text-muted text-center small">No feedback comments submitted yet. Use the form above to add feedback.</div>`;
    } else {
      commentsContainer.innerHTML = data.comments.map(c => `
        <div class="p-3 border rounded-3 mb-2 bg-light">
          <p class="text-dark small mb-1">"${c.text}"</p>
          <div class="text-muted small" style="font-size:0.72rem;">
            <i class="bi bi-person-check me-1 text-success"></i>Student Feedback &bull; ${c.date}
          </div>
        </div>
      `).join('');
    }
  }

  // Rating Chart
  const ctx = document.getElementById('feedbackDistChart');
  if (ctx && data.distribution) {
    if (feedbackChartInstance) {
      feedbackChartInstance.destroy();
    }
    feedbackChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
        datasets: [{
          data: [
            data.distribution[5] || 0,
            data.distribution[4] || 0,
            data.distribution[3] || 0,
            data.distribution[2] || 0,
            data.distribution[1] || 0
          ],
          backgroundColor: ['#16A34A', '#4338CA', '#6366F1', '#F59E0B', '#DC2626']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } } }
        }
      }
    });
  }
}
