/**
 * CourseFlow - Dashboard Controller (Simplified)
 * Handles both Faculty and Administrator dashboard views cleanly.
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!document.getElementById('dashboardRoot')) return;

  const courses = await CourseFlow.apiService.getCourses();
  const faculty = await CourseFlow.apiService.getFaculty();
  const currentUser = CourseFlow.apiService.getCurrentUser();

  // If Administrator Dashboard
  if (currentUser && currentUser.role === 'admin') {
    renderAdminDashboard(courses, faculty);
  } else {
    // Faculty Dashboard
    renderFacultyDashboard(courses);
  }
});

async function renderAdminDashboard(courses, faculty) {
  const totalFaculty = faculty.length;
  const totalCourses = courses.length;
  const completed = courses.filter(c => c.completion === 100).length;
  const inProgress = courses.filter(c => c.completion < 100).length;

  if (document.getElementById('adminStatFaculty')) {
    document.getElementById('adminStatFaculty').textContent = totalFaculty;
  }
  if (document.getElementById('adminStatCourses')) {
    document.getElementById('adminStatCourses').textContent = totalCourses;
  }
  if (document.getElementById('adminStatCompleted')) {
    document.getElementById('adminStatCompleted').textContent = completed;
  }
  if (document.getElementById('adminStatInProgress')) {
    document.getElementById('adminStatInProgress').textContent = inProgress;
  }

  const tbody = document.getElementById('adminCoursesTbody');
  if (tbody) {
    tbody.innerHTML = courses.map(c => `
      <tr>
        <td>
          <div class="fw-semibold text-dark">${c.code}</div>
          <div class="text-muted small" style="font-size:0.75rem;">${c.title}</div>
        </td>
        <td class="small text-secondary">${c.semester}</td>
        <td class="small text-dark"><i class="bi bi-person me-1 text-muted"></i>${c.faculty}</td>
        <td style="min-width: 140px;">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="small fw-semibold text-dark">${c.completion}%</span>
          </div>
          <div class="cf-progress">
            <div class="cf-progress-bar ${c.completion === 100 ? 'cf-progress-bar-success' : 'cf-progress-bar-indigo'}" 
                 style="width: ${c.completion}%"></div>
          </div>
        </td>
        <td>${CourseFlow.renderStatusBadge(c.status)}</td>
        <td class="text-end">
          <a href="/courses/${c.id}" class="btn btn-sm btn-outline-primary py-1 px-2" style="font-size:0.78rem;">
            <i class="bi bi-eye"></i> View
          </a>
        </td>
      </tr>
    `).join('');
  }
}

async function renderFacultyDashboard(courses) {
  const sessionPlans = await CourseFlow.apiService.getSessionPlans('CS301');
  const attainment = await CourseFlow.apiService.getAttainment('CS301');

  // Compute live statistics from store
  const totalAssigned = courses.length;
  const inProgress = courses.filter(c => c.status === 'In Progress' || c.status === 'Draft' || c.status === 'Under Review').length;
  const completed = courses.filter(c => c.status === 'Completed' || c.status === 'Approved').length;
  
  let lowAttainmentCount = 0;
  if (attainment && attainment.outcomes) {
    lowAttainmentCount = attainment.outcomes.filter(o => o.status === 'Below Target').length;
  }

  // Update stat widgets
  if (document.getElementById('statTotalCourses')) document.getElementById('statTotalCourses').textContent = totalAssigned;
  if (document.getElementById('statInProgress')) document.getElementById('statInProgress').textContent = inProgress;
  if (document.getElementById('statCompleted')) document.getElementById('statCompleted').textContent = completed;
  if (document.getElementById('statLowAttainment')) document.getElementById('statLowAttainment').textContent = lowAttainmentCount;

  // Render Charts
  renderCompletionChart(courses);
  renderAttainmentChart(attainment);

  // Render Course Table
  renderDashboardCourses(courses);

  // Render Upcoming Sessions
  renderUpcomingSessions(sessionPlans);

  // Render Attention Items
  renderAttentionItems(courses, attainment);
}

function renderCompletionChart(courses) {
  const ctx = document.getElementById('completionChart');
  if (!ctx) return;

  const labels = courses.map(c => c.code);
  const data = courses.map(c => c.completion);
  const backgroundColors = data.map(val => {
    if (val === 100) return '#059669'; // Emerald / Complete
    if (val >= 75) return '#2563EB';  // Institutional Blue
    if (val >= 50) return '#3B82F6';
    return '#D97706';                // Amber / In progress
  });

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Readiness %',
        data: data,
        backgroundColor: backgroundColors,
        borderRadius: 4,
        maxBarThickness: 28
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Course Handout Readiness: ${ctx.parsed.y}%`
          }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { stepSize: 25, callback: v => v + '%' },
          grid: { color: '#E5E7EB' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderAttainmentChart(attainment) {
  const ctx = document.getElementById('attainmentChart');
  if (!ctx || !attainment || !attainment.outcomes) return;

  const labels = attainment.outcomes.map(o => o.code);
  const targets = attainment.outcomes.map(o => o.target);
  const achieved = attainment.outcomes.map(o => o.achieved);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Target Benchmark (%)',
          data: targets,
          backgroundColor: '#E2E8F0',
          borderColor: '#CBD5E1',
          borderWidth: 1,
          borderRadius: 4,
          maxBarThickness: 24
        },
        {
          label: 'Achieved Average (%)',
          data: achieved,
          backgroundColor: '#4338CA',
          borderRadius: 4,
          maxBarThickness: 24
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { font: { family: 'Inter', size: 12 }, boxWidth: 12 }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20, callback: v => v + '%' },
          grid: { color: '#F1F5F9' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderDashboardCourses(courses) {
  const tbody = document.getElementById('dashboardCoursesTbody');
  if (!tbody) return;

  tbody.innerHTML = courses.map(c => `
    <tr>
      <td>
        <div class="fw-semibold text-dark">${c.code}</div>
        <div class="text-muted small" style="font-size:0.75rem;">${c.title}</div>
      </td>
      <td class="small text-secondary">${c.semester}</td>
      <td class="small text-secondary">${c.studentsCount} Students</td>
      <td style="min-width: 140px;">
        <div class="d-flex align-items-center justify-content-between mb-1">
          <span class="small fw-semibold text-dark">${c.completion}%</span>
        </div>
        <div class="cf-progress">
          <div class="cf-progress-bar ${c.completion === 100 ? 'cf-progress-bar-success' : c.completion < 50 ? 'cf-progress-bar-warning' : 'cf-progress-bar-indigo'}" 
               style="width: ${c.completion}%"></div>
        </div>
      </td>
      <td>${CourseFlow.renderStatusBadge(c.status)}</td>
      <td class="text-end">
        <a href="/courses/${c.id}" class="btn btn-sm btn-outline-primary py-1 px-2" style="font-size:0.78rem;">
          <i class="bi bi-eye"></i> View
        </a>
      </td>
    </tr>
  `).join('');
}

function renderUpcomingSessions(sessions) {
  const container = document.getElementById('upcomingSessionsContainer');
  if (!container) return;

  const upcoming = sessions.filter(s => s.status === 'Planned').slice(0, 3);
  if (upcoming.length === 0) {
    container.innerHTML = `<div class="text-muted small p-3 text-center">All planned sessions are up to date.</div>`;
    return;
  }

  container.innerHTML = upcoming.map(s => `
    <div class="d-flex align-items-start gap-3 p-3 border-bottom">
      <div class="bg-primary-subtle text-primary rounded-3 text-center px-2 py-1 flex-shrink-0" style="min-width: 48px;">
        <div class="fw-bold fs-6">#${s.sessionNo}</div>
        <div class="text-muted" style="font-size: 0.65rem;">SESSION</div>
      </div>
      <div class="flex-grow-1">
        <div class="fw-semibold text-dark small">${s.topic}</div>
        <div class="text-secondary small mt-1" style="font-size: 0.75rem;">
          <span class="me-2"><i class="bi bi-calendar3 me-1"></i>${s.date}</span>
          <span class="me-2"><i class="bi bi-clock me-1"></i>${s.duration}</span>
          <span class="badge bg-light text-dark border">${s.lo}</span>
        </div>
      </div>
      <span class="badge bg-warning-subtle text-warning border border-warning-subtle small">Planned</span>
    </div>
  `).join('');
}

function renderAttentionItems(courses, attainment) {
  const container = document.getElementById('attentionItemsContainer');
  if (!container) return;

  const items = [];
  
  // Courses with completion < 50%
  courses.filter(c => c.completion < 50).forEach(c => {
    items.push({
      type: 'warning',
      icon: 'bi-file-earmark-break text-warning',
      title: `${c.code}: Course File at ${c.completion}%`,
      desc: 'Checklist sections need completion.',
      link: `/course-file?course_id=${c.id}`
    });
  });

  // Low attainment outcomes
  if (attainment && attainment.outcomes) {
    attainment.outcomes.filter(o => o.status === 'Below Target').forEach(o => {
      items.push({
        type: 'danger',
        icon: 'bi-graph-down-arrow text-danger',
        title: `CS301: ${o.code} Attainment (${o.diff})`,
        desc: `Outcome achieved (${o.achieved}%) is below target (${o.target}%).`,
        link: `/attainment?course_id=CS301`
      });
    });
  }

  if (items.length === 0) {
    container.innerHTML = `<div class="text-muted small p-3 text-center">No urgent alerts found. All records meet requirements.</div>`;
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="d-flex align-items-center justify-content-between p-3 border-bottom">
      <div class="d-flex align-items-start gap-3">
        <i class="bi ${item.icon} fs-4 mt-n1"></i>
        <div>
          <div class="fw-semibold text-dark small">${item.title}</div>
          <div class="text-secondary small" style="font-size: 0.76rem;">${item.desc}</div>
        </div>
      </div>
      <a href="${item.link}" class="btn btn-sm btn-outline-secondary py-1 px-2" style="font-size: 0.75rem;">View</a>
    </div>
  `).join('');
}
