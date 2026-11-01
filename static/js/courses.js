/**
 * CourseFlow - Courses Management Controller
 */

let allCourses = [];
let currentFilter = {
  search: '',
  semester: '',
  year: '',
  status: ''
};
let viewMode = 'table'; // 'table' or 'grid'

document.addEventListener('DOMContentLoaded', async () => {
  if (!document.getElementById('coursesRoot')) return;

  await loadCourses();
  setupCourseEventListeners();
});

async function loadCourses() {
  allCourses = await CourseFlow.apiService.getCourses();
  renderCourses();
}

function setupCourseEventListeners() {
  // Search input
  const searchInput = document.getElementById('courseSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentFilter.search = e.target.value.toLowerCase().trim();
      renderCourses();
    });
  }

  // Filters
  const semesterFilter = document.getElementById('filterSemester');
  if (semesterFilter) {
    semesterFilter.addEventListener('change', (e) => {
      currentFilter.semester = e.target.value;
      renderCourses();
    });
  }

  const yearFilter = document.getElementById('filterYear');
  if (yearFilter) {
    yearFilter.addEventListener('change', (e) => {
      currentFilter.year = e.target.value;
      renderCourses();
    });
  }

  const statusFilter = document.getElementById('filterStatus');
  if (statusFilter) {
    statusFilter.addEventListener('change', (e) => {
      currentFilter.status = e.target.value;
      renderCourses();
    });
  }

  // Clear filters
  const clearBtn = document.getElementById('clearFiltersBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      currentFilter = { search: '', semester: '', year: '', status: '' };
      if (searchInput) searchInput.value = '';
      if (semesterFilter) semesterFilter.value = '';
      if (yearFilter) yearFilter.value = '';
      if (statusFilter) statusFilter.value = '';
      renderCourses();
    });
  }

  // View mode switcher
  const viewTableBtn = document.getElementById('viewTableBtn');
  const viewGridBtn = document.getElementById('viewGridBtn');
  if (viewTableBtn && viewGridBtn) {
    viewTableBtn.addEventListener('click', () => {
      viewMode = 'table';
      viewTableBtn.classList.add('active');
      viewGridBtn.classList.remove('active');
      renderCourses();
    });
    viewGridBtn.addEventListener('click', () => {
      viewMode = 'grid';
      viewGridBtn.classList.add('active');
      viewTableBtn.classList.remove('active');
      renderCourses();
    });
  }

  // Course Form Submit (Add / Edit)
  const courseForm = document.getElementById('courseModalForm');
  if (courseForm) {
    courseForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!courseForm.checkValidity()) {
        courseForm.classList.add('was-validated');
        return;
      }

      const id = document.getElementById('courseFormId').value;
      const code = document.getElementById('courseFormCode').value.trim().toUpperCase();
      const title = document.getElementById('courseFormTitle').value.trim();
      const semester = document.getElementById('courseFormSemester').value;
      const academicYear = document.getElementById('courseFormYear').value;
      const faculty = document.getElementById('courseFormFaculty').value;
      const credits = parseInt(document.getElementById('courseFormCredits').value, 10) || 4;
      const studentsCount = parseInt(document.getElementById('courseFormStudents').value, 10) || 50;
      const description = document.getElementById('courseFormDesc').value.trim();

      // M2-TC03: Reject duplicate course code
      const isDuplicate = allCourses.some(c => c.code.toUpperCase() === code && (!id || c.id !== id));
      if (isDuplicate) {
        CourseFlow.showToast(`Course code "${code}" already exists. Duplicate course codes are not allowed.`, 'danger', 'Duplicate Code');
        return;
      }

      const newCourse = {
        id: id || code,
        isEdit: !!id,
        code,
        title,
        semester,
        academicYear,
        faculty,
        facultyEmail: 'faculty@courseflow.demo',
        credits,
        studentsCount,
        description,
        completion: id ? (allCourses.find(c => c.id === id)?.completion || 50) : 10,
        status: id ? (allCourses.find(c => c.id === id)?.status || 'Draft') : 'Draft',
        department: 'Computer Science & Engineering'
      };

      try {
        await CourseFlow.apiService.saveCourse(newCourse);
        CourseFlow.showToast(id ? 'Course updated successfully' : 'Course created successfully', 'success');

        const modalEl = document.getElementById('courseModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        await loadCourses();
      } catch (err) {
        CourseFlow.showToast(err.message || 'Error saving course', 'danger', 'Error');
      }
    });
  }
}

function filterCoursesList() {
  return allCourses.filter(c => {
    const matchSearch = !currentFilter.search || 
      c.code.toLowerCase().includes(currentFilter.search) || 
      c.title.toLowerCase().includes(currentFilter.search) ||
      c.faculty.toLowerCase().includes(currentFilter.search);

    const matchSem = !currentFilter.semester || c.semester === currentFilter.semester;
    const matchYear = !currentFilter.year || c.academicYear === currentFilter.year;
    const matchStatus = !currentFilter.status || c.status === currentFilter.status;

    return matchSearch && matchSem && matchYear && matchStatus;
  });
}

function renderCourses() {
  const filtered = filterCoursesList();
  const tableContainer = document.getElementById('coursesTableView');
  const gridContainer = document.getElementById('coursesGridView');
  const emptyState = document.getElementById('coursesEmptyState');
  const countEl = document.getElementById('coursesCountLabel');

  if (countEl) {
    countEl.textContent = `Showing ${filtered.length} of ${allCourses.length} courses`;
  }

  if (filtered.length === 0) {
    if (tableContainer) tableContainer.style.display = 'none';
    if (gridContainer) gridContainer.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';

  if (viewMode === 'table') {
    if (tableContainer) tableContainer.style.display = 'block';
    if (gridContainer) gridContainer.style.display = 'none';
    renderTableView(filtered);
  } else {
    if (tableContainer) tableContainer.style.display = 'none';
    if (gridContainer) gridContainer.style.display = 'flex';
    renderGridView(filtered);
  }
}

function renderTableView(courses) {
  const tbody = document.getElementById('coursesTableTbody');
  if (!tbody) return;

  tbody.innerHTML = courses.map(c => `
    <tr>
      <td>
        <a href="/courses/${c.id}" class="fw-bold text-dark text-decoration-none">${c.code}</a>
        <div class="text-secondary small">${c.title}</div>
      </td>
      <td class="small text-muted">${c.semester}</td>
      <td class="small text-muted">${c.academicYear}</td>
      <td class="small text-dark">
        <i class="bi bi-person me-1 text-muted"></i>${c.faculty}
      </td>
      <td class="small text-center">${c.studentsCount}</td>
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
        <div class="dropdown">
          <button class="btn btn-sm btn-light border py-1 px-2" type="button" data-bs-toggle="dropdown">
            <i class="bi bi-three-dots"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li><a class="dropdown-item small" href="/courses/${c.id}"><i class="bi bi-eye me-2"></i>View Course Details</a></li>
            <li><a class="dropdown-item small" href="/course-file?course_id=${c.id}"><i class="bi bi-folder2-open me-2"></i>Course File Checklist</a></li>
            <li><button class="dropdown-item small" onclick="openEditCourseModal('${c.id}')"><i class="bi bi-pencil me-2"></i>Edit Course Info</button></li>
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item small text-danger" onclick="deleteCourse('${c.id}')"><i class="bi bi-trash me-2"></i>Delete Course</button></li>
          </ul>
        </div>
      </td>
    </tr>
  `).join('');
}

function renderGridView(courses) {
  const grid = document.getElementById('coursesGridView');
  if (!grid) return;

  grid.innerHTML = courses.map(c => `
    <div class="col-md-6 col-lg-4 mb-4">
      <div class="cf-card h-100 p-3 d-flex flex-direction-column justify-content-between">
        <div>
          <div class="d-flex justify-content-between align-items-start mb-2">
            <span class="badge bg-primary-subtle text-primary fw-bold px-2 py-1">${c.code}</span>
            ${CourseFlow.renderStatusBadge(c.status)}
          </div>
          <h6 class="fw-bold text-dark mb-1">${c.title}</h6>
          <p class="text-secondary small mb-3" style="min-height: 38px; font-size: 0.8rem;">${c.description.substring(0, 85)}...</p>
          
          <div class="bg-light rounded p-2 small mb-3">
            <div class="d-flex justify-content-between text-muted mb-1">
              <span>Semester:</span> <strong class="text-dark">${c.semester}</strong>
            </div>
            <div class="d-flex justify-content-between text-muted mb-1">
              <span>Academic Year:</span> <strong class="text-dark">${c.academicYear}</strong>
            </div>
            <div class="d-flex justify-content-between text-muted">
              <span>Enrolled:</span> <strong class="text-dark">${c.studentsCount} Students</strong>
            </div>
          </div>
        </div>

        <div>
          <div class="d-flex justify-content-between small mb-1">
            <span class="text-muted">Course File Readiness</span>
            <span class="fw-bold">${c.completion}%</span>
          </div>
          <div class="cf-progress mb-3">
            <div class="cf-progress-bar ${c.completion === 100 ? 'cf-progress-bar-success' : c.completion < 50 ? 'cf-progress-bar-warning' : 'cf-progress-bar-indigo'}" 
                 style="width: ${c.completion}%"></div>
          </div>

          <div class="d-flex gap-2">
            <a href="/courses/${c.id}" class="btn btn-sm btn-primary flex-grow-1">View Details</a>
            <button class="btn btn-sm btn-outline-secondary" onclick="openEditCourseModal('${c.id}')"><i class="bi bi-pencil"></i></button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteCourse('${c.id}')"><i class="bi bi-trash"></i></button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

window.openAddCourseModal = function() {
  const form = document.getElementById('courseModalForm');
  if (!form) return;
  form.reset();
  form.classList.remove('was-validated');
  document.getElementById('courseFormId').value = '';
  document.getElementById('courseModalTitle').textContent = 'Add New Course';
  document.getElementById('courseFormCode').disabled = false;
  
  const modal = new bootstrap.Modal(document.getElementById('courseModal'));
  modal.show();
};

window.openEditCourseModal = function(id) {
  const c = allCourses.find(item => item.id === id);
  if (!c) return;

  const form = document.getElementById('courseModalForm');
  form.classList.remove('was-validated');
  document.getElementById('courseFormId').value = c.id;
  document.getElementById('courseModalTitle').textContent = `Edit Course: ${c.code}`;
  
  document.getElementById('courseFormCode').value = c.code;
  document.getElementById('courseFormCode').disabled = true;
  document.getElementById('courseFormTitle').value = c.title;
  document.getElementById('courseFormSemester').value = c.semester;
  document.getElementById('courseFormYear').value = c.academicYear;
  document.getElementById('courseFormFaculty').value = c.faculty;
  document.getElementById('courseFormCredits').value = c.credits || 4;
  document.getElementById('courseFormStudents').value = c.studentsCount || 50;
  document.getElementById('courseFormDesc').value = c.description || '';

  const modal = new bootstrap.Modal(document.getElementById('courseModal'));
  modal.show();
};

window.deleteCourse = function(id) {
  CourseFlow.confirmAction(
    `Are you sure you want to delete course ${id}? This action will remove all linked syllabus and assessment records in demo mode.`,
    async () => {
      await CourseFlow.apiService.deleteCourse(id);
      CourseFlow.showToast(`Course ${id} deleted successfully`, 'success');
      await loadCourses();
    },
    'Delete Course Confirmation'
  );
};
