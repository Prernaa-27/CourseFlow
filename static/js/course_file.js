/**
 * CourseFlow - Course File Generator & Lifecycle Manager
 */

let currentCourseFile = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (document.getElementById('courseFileRoot')) {
    initCourseFilePage();
  } else if (document.getElementById('courseFilePreviewRoot')) {
    initCourseFilePreviewPage();
  }
});

async function initCourseFilePage() {
  const courseSelect = document.getElementById('cfCourseSelect');
  const urlParams = new URLSearchParams(window.location.search);
  let currentCourse = urlParams.get('course_id') || (courseSelect ? courseSelect.value : 'CS301');

  if (courseSelect) {
    courseSelect.value = currentCourse;
    courseSelect.addEventListener('change', (e) => {
      window.location.search = `?course_id=${e.target.value}`;
    });
  }

  async function load() {
    currentCourseFile = await CourseFlow.apiService.getCourseFile(currentCourse);
    const course = await CourseFlow.apiService.getCourse(currentCourse);
    if (course && document.getElementById('cfFacultyName')) {
      document.getElementById('cfFacultyName').textContent = course.faculty;
    }
    renderChecklist();
  }

  // Mark Complete button
  const markCompleteBtn = document.getElementById('markCompleteBtn');
  if (markCompleteBtn) {
    markCompleteBtn.addEventListener('click', async () => {
      await CourseFlow.apiService.updateCourseFileStatus(currentCourse, 'Completed');
      CourseFlow.showToast('Course file status marked as Completed.', 'success', 'Status Updated');
      await load();
    });
  }

  // Generate button
  const generateBtn = document.getElementById('generateDossierBtn');
  if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
      const incomplete = currentCourseFile.checklist.filter(i => !i.completed);
      if (incomplete.length > 0) {
        CourseFlow.showToast(
          `Notice: ${incomplete.length} section(s) still marked incomplete. Generating draft preview...`,
          'warning',
          'Draft Preview'
        );
      } else {
        await CourseFlow.apiService.updateCourseFileStatus(currentCourse, 'Completed');
        CourseFlow.showToast('Course handout generated successfully! Opening preview...', 'success', 'Handout Generated');
      }

      setTimeout(() => {
        window.location.href = `/course-file/preview?course_id=${currentCourse}`;
      }, 600);
    });
  }

  await load();
}

function renderChecklist() {
  if (!currentCourseFile) return;

  const container = document.getElementById('cfChecklistContainer');
  if (!container) return;

  const total = currentCourseFile.checklist.length;
  const completed = currentCourseFile.checklist.filter(i => i.completed).length;
  const pct = Math.round((completed / total) * 100);

  // Update gauges
  if (document.getElementById('cfCompletionPctLabel')) {
    document.getElementById('cfCompletionPctLabel').textContent = `${pct}%`;
  }
  if (document.getElementById('cfCompletionProgressBar')) {
    document.getElementById('cfCompletionProgressBar').style.width = `${pct}%`;
  }
  if (document.getElementById('cfStatusBadgeContainer')) {
    document.getElementById('cfStatusBadgeContainer').innerHTML = CourseFlow.renderStatusBadge(currentCourseFile.status);
  }

  container.innerHTML = currentCourseFile.checklist.map(item => `
    <div class="checklist-item ${item.completed ? 'border-success-subtle' : 'border-danger-subtle'}">
      <div class="d-flex align-items-center gap-3">
        <div class="checklist-status-icon ${item.completed ? 'complete' : 'missing'}">
          <i class="bi ${item.completed ? 'bi-check2' : 'bi-exclamation-triangle'}"></i>
        </div>
        <div>
          <div class="fw-semibold text-dark fs-6">
            ${item.title}
          </div>
          <div class="text-secondary small mt-0">${item.notes}</div>
        </div>
      </div>
      <div class="form-check form-switch me-2">
        <input class="form-check-input" type="checkbox" role="switch" ${item.completed ? 'checked' : ''} 
               onchange="toggleChecklistItem('${item.id}', this.checked)">
      </div>
    </div>
  `).join('');
}

window.toggleChecklistItem = async function(checkId, isChecked) {
  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get('course_id') || 'CS301';

  await CourseFlow.apiService.updateChecklistItem(courseId, checkId, isChecked);
  currentCourseFile = await CourseFlow.apiService.getCourseFile(courseId);
  renderChecklist();
  CourseFlow.showToast(`Checklist section updated`, 'info');
};

// ==========================================================================
// COURSE FILE PREVIEW
// ==========================================================================
async function initCourseFilePreviewPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get('course_id') || 'CS301';

  let course = await CourseFlow.apiService.getCourse(courseId);
  if (!course) {
    course = await CourseFlow.apiService.getCourse('CS301');
  }
  const syllabus = await CourseFlow.apiService.getSyllabus(courseId);
  const sessionPlans = await CourseFlow.apiService.getSessionPlans(courseId);
  const students = await CourseFlow.apiService.getStudents(courseId);
  const attendance = await CourseFlow.apiService.getAttendance(courseId);
  const assessments = await CourseFlow.apiService.getAssessments(courseId);
  const feedback = await CourseFlow.apiService.getFeedback(courseId);
  const outcomes = await CourseFlow.apiService.getOutcomes(courseId);
  const attainment = await CourseFlow.apiService.getAttainment(courseId);

  // Fill Cover
  if (course) {
    document.querySelectorAll('.preview-course-code').forEach(el => el.textContent = course.code);
    document.querySelectorAll('.preview-course-title').forEach(el => el.textContent = course.title);
    document.querySelectorAll('.preview-course-sem').forEach(el => el.textContent = course.semester);
    document.querySelectorAll('.preview-course-year').forEach(el => el.textContent = course.academicYear);
    document.querySelectorAll('.preview-course-faculty').forEach(el => el.textContent = course.faculty);
    document.querySelectorAll('.preview-course-dept').forEach(el => el.textContent = course.department);
    document.querySelectorAll('.preview-course-desc').forEach(el => el.textContent = course.description);
  }

  // Print Action
  const printBtn = document.getElementById('printPdfBtn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  // Download Action
  const dlBtn = document.getElementById('downloadPdfBtn');
  if (dlBtn) {
    dlBtn.addEventListener('click', () => {
      window.print();
    });
  }

  // 1. Render Syllabus Section
  const sylTable = document.getElementById('previewSyllabusTbody');
  if (sylTable) {
    const sylList = (syllabus && syllabus.length > 0) ? syllabus : await CourseFlow.apiService.getSyllabus('CS301');
    if (sylList && sylList.length > 0) {
      sylTable.innerHTML = sylList.map(u => `
        <tr>
          <td class="fw-bold text-center">Unit ${u.unit}</td>
          <td>
            <div class="fw-semibold text-dark">${u.title}</div>
            <div class="small text-muted">${u.topics || ''}</div>
          </td>
          <td class="text-center fw-semibold">${u.hours} hrs</td>
          <td class="text-center"><span class="badge bg-light text-dark border">${u.outcomes || 'CO1'}</span></td>
        </tr>
      `).join('');
    }
  }

  // 2. Render Session Plans
  const sessTable = document.getElementById('previewSessionsTbody');
  if (sessTable) {
    const sessList = (sessionPlans && sessionPlans.length > 0) ? sessionPlans : await CourseFlow.apiService.getSessionPlans('CS301');
    if (sessList && sessList.length > 0) {
      sessTable.innerHTML = sessList.map(s => `
        <tr>
          <td class="text-center fw-bold">#${s.sessionNo}</td>
          <td>
            <div class="fw-semibold text-dark">${s.topic}</div>
            <div class="small text-muted" style="font-size:0.75rem;">${s.resources || ''}</div>
          </td>
          <td class="text-center"><span class="badge bg-light text-dark border">${s.lo || 'CO1'}</span></td>
          <td class="small text-muted">${s.date || ''}</td>
          <td class="small text-secondary">${s.method || 'Interactive Lecture'}</td>
          <td class="text-center">
            <span class="badge ${s.status === 'Completed' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'}">
              ${s.status || 'Planned'}
            </span>
          </td>
        </tr>
      `).join('');
    }
  }

  // 3. Render Students & Attendance
  const studTable = document.getElementById('previewStudentsTbody');
  if (studTable) {
    const studentList = (students && students.length > 0) ? students : await CourseFlow.apiService.getStudents('CS301');
    const attData = (attendance && attendance.records && Object.keys(attendance.records).length > 0) ? attendance : await CourseFlow.apiService.getAttendance('CS301');

    if (studentList && studentList.length > 0) {
      studTable.innerHTML = studentList.map(st => {
        const records = (attData && attData.records && attData.records[st.id]) ? attData.records[st.id] : [];
        const totalDates = (attData && attData.dates && attData.dates.length > 0) ? attData.dates.length : (records.length || 7);
        const presentCount = records.filter(x => x === 'P').length;
        const pct = totalDates > 0 ? Math.round((presentCount / totalDates) * 100) : 85;
        const isShortage = pct < 75;

        return `
          <tr>
            <td class="fw-bold">${st.id}</td>
            <td>
              <div class="fw-semibold text-dark">${st.name}</div>
              <div class="text-muted small" style="font-size:0.75rem;">${st.email}</div>
            </td>
            <td class="text-center">
              <span class="badge ${isShortage ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-success-subtle text-success border border-success-subtle'}">
                ${isShortage ? 'Shortage (<75%)' : 'Regular (>=75%)'}
              </span>
            </td>
            <td class="text-center fw-bold ${isShortage ? 'text-danger' : 'text-dark'}">${pct}%</td>
          </tr>
        `;
      }).join('');
    }
  }

  // 4. Render Assessments
  const asmTable = document.getElementById('previewAssessmentsTbody');
  if (asmTable) {
    const asmList = (assessments && assessments.length > 0) ? assessments : await CourseFlow.apiService.getAssessments('CS301');
    if (asmList && asmList.length > 0) {
      asmTable.innerHTML = asmList.map(a => `
        <tr>
          <td class="fw-semibold text-dark">${a.title}</td>
          <td><span class="badge bg-light text-dark border">${a.type}</span></td>
          <td class="text-center fw-bold">${a.maxMarks}</td>
          <td class="text-center">${a.weightage}%</td>
          <td class="text-center"><span class="badge bg-primary-subtle text-primary">${a.co}</span></td>
        </tr>
      `).join('');
    }
  }

  // 5. Render Feedback Summary
  const fbContainer = document.getElementById('previewFeedbackContainer');
  if (fbContainer) {
    const fbData = (feedback && feedback.totalResponses) ? feedback : await CourseFlow.apiService.getFeedback('CS301');
    if (fbData) {
      const avgRating = fbData.averageRating || 4.5;
      const fullStars = Math.round(avgRating);
      const stars = '★'.repeat(fullStars) + '☆'.repeat(5 - fullStars);
      const comments = (fbData.comments && fbData.comments.length > 0) ? fbData.comments : [];
      const recentComments = comments.slice(0, 3).map(c => `
        <li class="mb-2">
          <span class="text-dark fw-semibold">"${c.text || c.comment || 'Practical labs were very helpful.'}"</span>
          <span class="badge bg-light text-muted ms-1">${c.date || 'Semester Survey'}</span>
        </li>
      `).join('');

      fbContainer.innerHTML = `
        <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between pb-2 mb-3 border-bottom gap-2">
          <div>
            <strong class="text-dark">Overall Student Satisfaction Rating:</strong>
            <span class="text-warning fs-5 ms-1">${stars}</span>
            <span class="fw-bold text-primary ms-1">${avgRating.toFixed(1)} / 5.0</span>
          </div>
          <div class="text-muted small">Total Survey Responses: <strong>${fbData.totalResponses || 4} Students</strong></div>
        </div>
        <div>
          <strong class="d-block mb-1 text-dark small"><i class="bi bi-chat-quote-fill text-primary me-1"></i>Sample Student Exit Feedback:</strong>
          <ul class="mb-0 ps-3 small text-secondary">
            ${recentComments || '<li class="text-muted">Positive feedback on laboratory exercises and sprint planning.</li>'}
          </ul>
        </div>
      `;
    }
  }

  // 6. Render Outcomes Mapping
  const outTable = document.getElementById('previewOutcomesTbody');
  if (outTable) {
    let outData = outcomes;
    if (!outData || !outData.cos || outData.cos.length === 0) {
      outData = await CourseFlow.apiService.getOutcomes('CS301');
    }
    if (outData && outData.cos && outData.cos.length > 0) {
      const coList = outData.cos;
      const mapping = outData.mapping || {};

      outTable.innerHTML = coList.map(co => {
        const m = mapping[co.code] || {};
        const getVal = (target) => (m[target] !== undefined && m[target] > 0) ? m[target] : '-';
        return `
          <tr>
            <td class="text-start">
              <span class="badge bg-primary-subtle text-primary fw-bold me-1">${co.code}</span>
              <span class="small fw-semibold text-dark">${co.text || co.statement || ''}</span>
            </td>
            <td class="fw-semibold">${getVal('PO1')}</td>
            <td class="fw-semibold">${getVal('PO2')}</td>
            <td class="fw-semibold">${getVal('PO3')}</td>
            <td class="fw-semibold">${getVal('PO4')}</td>
            <td class="fw-semibold">${getVal('PO5')}</td>
            <td class="fw-semibold">${getVal('PSO1')}</td>
            <td class="fw-semibold">${getVal('PSO2')}</td>
          </tr>
        `;
      }).join('');
    }
  }

  // 7. Render Attainment Summary
  const attTable = document.getElementById('previewAttainmentTbody');
  if (attTable) {
    let attData = attainment;
    if (!attData || !attData.outcomes || attData.outcomes.length === 0) {
      attData = await CourseFlow.apiService.getAttainment('CS301');
    }
    if (attData && attData.outcomes && attData.outcomes.length > 0) {
      attTable.innerHTML = attData.outcomes.map(o => {
        const target = o.target !== undefined ? o.target : 70;
        const avg = o.achieved !== undefined ? o.achieved : (o.internal || 75);
        const diffNum = parseFloat((avg - target).toFixed(1));
        const meets = avg >= target;
        const diffStr = diffNum >= 0 ? `+${diffNum}%` : `${diffNum}%`;
        const statusClass = meets ? 'text-success' : 'text-danger';
        const statusText = meets ? 'Meets Target' : 'Below Target';
        const badgeClass = meets ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-danger-subtle text-danger border border-danger-subtle';

        return `
          <tr>
            <td class="fw-bold text-dark">${o.code}</td>
            <td class="text-center">${target}%</td>
            <td class="text-center fw-semibold text-dark">${avg}%</td>
            <td class="text-center fw-bold ${statusClass}">${diffStr}</td>
            <td class="text-center">
              <span class="badge ${badgeClass}">${statusText}</span>
            </td>
          </tr>
        `;
      }).join('');
    }
  }
}