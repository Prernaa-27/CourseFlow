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
        CourseFlow.showToast('Course file generated successfully! Opening preview...', 'success', 'Dossier Generated');
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

  const course = await CourseFlow.apiService.getCourse(courseId);
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
  if (sylTable && syllabus) {
    sylTable.innerHTML = syllabus.map(u => `
      <tr>
        <td class="fw-bold">Unit ${u.unit}</td>
        <td><strong>${u.title}</strong><div class="small text-muted">${u.topics}</div></td>
        <td class="text-center">${u.hours} hrs</td>
        <td class="text-center">${u.outcomes}</td>
      </tr>
    `).join('');
  }

  // 2. Render Session Plans
  const sessTable = document.getElementById('previewSessionsTbody');
  if (sessTable && sessionPlans) {
    sessTable.innerHTML = sessionPlans.map(s => `
      <tr>
        <td class="text-center">#${s.sessionNo}</td>
        <td>${s.topic}</td>
        <td class="text-center">${s.lo}</td>
        <td>${s.date}</td>
        <td>${s.method}</td>
        <td class="text-center"><span class="badge ${s.status === 'Completed' ? 'bg-success' : 'bg-secondary'}">${s.status}</span></td>
      </tr>
    `).join('');
  }

  // 3. Render Students & Attendance
  const studTable = document.getElementById('previewStudentsTbody');
  if (studTable && students) {
    studTable.innerHTML = students.map(st => {
      let presentCount = 0;
      let totalCount = 0;
      if (attendance && attendance.records) {
        attendance.records.forEach(session => {
          if (session.attendance && session.attendance[st.id]) {
            totalCount++;
            if (session.attendance[st.id] === 'P') presentCount++;
          }
        });
      }
      const pct = totalCount > 0 ? Math.round((presentCount / totalCount) * 100) : 85;
      return `
        <tr>
          <td class="fw-bold">${st.rollNo}</td>
          <td>${st.name}</td>
          <td class="text-center"><span class="badge bg-success-subtle text-success">Good</span></td>
          <td class="text-center fw-bold">${pct}%</td>
        </tr>
      `;
    }).join('');
  }

  // 4. Render Assessments
  const asmTable = document.getElementById('previewAssessmentsTbody');
  if (asmTable && assessments) {
    asmTable.innerHTML = assessments.map(a => `
      <tr>
        <td class="fw-semibold">${a.title}</td>
        <td>${a.type}</td>
        <td class="text-center">${a.maxMarks}</td>
        <td class="text-center">${a.weightage}%</td>
        <td class="text-center">${a.co}</td>
      </tr>
    `).join('');
  }

  // 5. Render Feedback Summary
  const fbContainer = document.getElementById('previewFeedbackContainer');
  if (fbContainer && feedback) {
    const stars = '★'.repeat(Math.round(feedback.averageRating)) + '☆'.repeat(5 - Math.round(feedback.averageRating));
    const recentComments = feedback.comments && feedback.comments.length > 0 
      ? feedback.comments.slice(0, 3).map(c => `<li class="mb-1 text-secondary">"${c.comment}" <span class="badge bg-light text-dark ms-1">${c.rating}★</span></li>`).join('')
      : '<li class="text-muted">No comments submitted yet.</li>';

    fbContainer.innerHTML = `
      <div class="d-flex align-items-center justify-content-between mb-2">
        <div><strong>Overall Student Satisfaction Rating:</strong> <span class="text-warning fs-6">${stars}</span> (${feedback.averageRating} / 5.0)</div>
        <div class="text-muted">Responses: ${feedback.totalResponses} students</div>
      </div>
      <div class="mt-2">
        <strong class="d-block mb-1">Recent Student Feedback Comments:</strong>
        <ul class="mb-0 ps-3">
          ${recentComments}
        </ul>
      </div>
    `;
  }

  // 6. Render Outcomes Mapping
  const outTable = document.getElementById('previewOutcomesTbody');
  if (outTable && outcomes) {
    outTable.innerHTML = outcomes.map(co => {
      const getVal = (poKey) => (co.mapping && co.mapping[poKey]) ? co.mapping[poKey] : '-';
      return `
        <tr>
          <td class="text-start fw-semibold">${co.code}: ${co.statement}</td>
          <td>${getVal('PO1')}</td>
          <td>${getVal('PO2')}</td>
          <td>${getVal('PO3')}</td>
          <td>${getVal('PO4')}</td>
          <td>${getVal('PO5')}</td>
          <td>${getVal('PSO1')}</td>
          <td>${getVal('PSO2')}</td>
        </tr>
      `;
    }).join('');
  }

  // 7. Render Attainment Summary
  const attTable = document.getElementById('previewAttainmentTbody');
  if (attTable && attainment && attainment.outcomes) {
    attTable.innerHTML = attainment.outcomes.map(o => {
      const avg = o.achieved || o.internal || 75;
      const diff = avg - o.target;
      const diffStr = diff >= 0 ? `+${diff}%` : `${diff}%`;
      const statusClass = diff >= 0 ? 'text-success' : 'text-danger';
      const statusText = diff >= 0 ? 'Meets Target' : 'Needs Attention';

      return `
        <tr>
          <td class="fw-bold">${o.code}</td>
          <td class="text-center">${o.target}%</td>
          <td class="text-center fw-semibold">${avg}%</td>
          <td class="text-center ${statusClass} fw-bold">${diffStr}</td>
          <td class="text-center ${statusClass} fw-bold">${statusText}</td>
        </tr>
      `;
    }).join('');
  }
}
