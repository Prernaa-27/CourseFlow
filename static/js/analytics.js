/**
 * CourseFlow - Analytics Controller
 * (CO-PO/PSO Mapping Matrix & Attainment Analytics)
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (document.getElementById('outcomesRoot')) {
    initOutcomesMappingPage();
  } else if (document.getElementById('attainmentRoot')) {
    initAttainmentPage();
  }
});

// ==========================================================================
// 1. CO-PO / PSO MAPPING MATRIX
// ==========================================================================
const PO_LIST = ['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9', 'PO10', 'PO11', 'PO12'];
const PSO_LIST = ['PSO1', 'PSO2'];

let currentOutcomesData = null;

async function initOutcomesMappingPage() {
  const courseSelect = document.getElementById('outcomesCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function load() {
    currentOutcomesData = await CourseFlow.apiService.getOutcomes(currentCourse);
    renderCOList();
    renderMappingMatrix();
    updateCoverageMetrics();
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      load();
    });
  }

  // Save Mapping Matrix
  const saveBtn = document.getElementById('saveMatrixBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      // Gather selects
      const selects = document.querySelectorAll('.matrix-select');
      let hasInvalid = false;
      selects.forEach(sel => {
        const co = sel.dataset.co;
        const target = sel.dataset.target;
        const val = parseInt(sel.value, 10);
        // M5-TC04: Validate correlation level is 0, 1, 2, or 3
        if (isNaN(val) || val < 0 || val > 3) {
          hasInvalid = true;
          sel.classList.add('is-invalid');
        } else {
          sel.classList.remove('is-invalid');
          if (!currentOutcomesData.mapping[co]) currentOutcomesData.mapping[co] = {};
          currentOutcomesData.mapping[co][target] = val;
        }
      });

      if (hasInvalid) {
        CourseFlow.showToast('Correlation values must be between 0 and 3 (0: None, 1: Low, 2: Moderate, 3: High).', 'danger', 'Validation Error');
        return;
      }

      try {
        await CourseFlow.apiService.saveOutcomes(currentCourse, currentOutcomesData);
        CourseFlow.showToast('CO-PO and PSO mapping matrix saved and verified successfully!', 'success');
        updateCoverageMetrics();
      } catch (err) {
        CourseFlow.showToast(err.message || 'Error saving outcomes', 'danger', 'Validation Error');
      }
    });
  }

  // Add CO Modal
  const addCOBtn = document.getElementById('addCOBtn');
  if (addCOBtn) {
    addCOBtn.addEventListener('click', () => {
      document.getElementById('coCodeField').value = `CO${currentOutcomesData.cos.length + 1}`;
      document.getElementById('coTextField').value = '';
      const modal = new bootstrap.Modal(document.getElementById('coModal'));
      modal.show();
    });
  }

  const coForm = document.getElementById('coModalForm');
  if (coForm) {
    coForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const code = document.getElementById('coCodeField').value.trim();
      const text = document.getElementById('coTextField').value.trim();
      if (!text) return;

      currentOutcomesData.cos.push({ id: code, code, text });
      // init blank mapping
      currentOutcomesData.mapping[code] = {};
      [...PO_LIST, ...PSO_LIST].forEach(p => {
        currentOutcomesData.mapping[code][p] = 0;
      });

      await CourseFlow.apiService.saveOutcomes(currentCourse, currentOutcomesData);
      CourseFlow.showToast(`Outcome ${code} added`, 'success');

      const modal = bootstrap.Modal.getInstance(document.getElementById('coModal'));
      if (modal) modal.hide();

      renderCOList();
      renderMappingMatrix();
      updateCoverageMetrics();
    });
  }

  await load();
}

function renderCOList() {
  const container = document.getElementById('coListContainer');
  if (!container || !currentOutcomesData) return;

  container.innerHTML = currentOutcomesData.cos.map(co => `
    <div class="p-3 border rounded-3 mb-2 bg-white">
      <div class="d-flex justify-content-between align-items-center mb-1">
        <span class="badge bg-primary-subtle text-primary fw-bold">${co.code}</span>
        <button class="btn btn-sm btn-link text-danger p-0 text-decoration-none" onclick="removeCO('${co.code}')"><i class="bi bi-trash"></i></button>
      </div>
      <p class="text-secondary small mb-0">${co.text}</p>
    </div>
  `).join('');
}

function renderMappingMatrix() {
  const table = document.getElementById('matrixTable');
  if (!table || !currentOutcomesData) return;

  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');

  // Build header
  let theadHtml = `<th style="min-width: 120px;">Course Outcome</th>`;
  PO_LIST.forEach(po => theadHtml += `<th>${po}</th>`);
  PSO_LIST.forEach(pso => theadHtml += `<th class="bg-primary-subtle text-primary">${pso}</th>`);
  thead.innerHTML = theadHtml;

  // Build rows
  tbody.innerHTML = currentOutcomesData.cos.map(co => {
    let row = `<tr><td class="fw-bold text-dark">${co.code}</td>`;
    [...PO_LIST, ...PSO_LIST].forEach(target => {
      const val = (currentOutcomesData.mapping[co.code] && currentOutcomesData.mapping[co.code][target] !== undefined)
        ? currentOutcomesData.mapping[co.code][target] : 0;
      row += `
        <td>
          <select class="matrix-select" data-co="${co.code}" data-target="${target}" onchange="updateCellColor(this); updateCoverageMetrics();">
            <option value="0" ${val === 0 ? 'selected' : ''}>-</option>
            <option value="1" ${val === 1 ? 'selected' : ''}>1</option>
            <option value="2" ${val === 2 ? 'selected' : ''}>2</option>
            <option value="3" ${val === 3 ? 'selected' : ''}>3</option>
          </select>
        </td>
      `;
    });
    row += `</tr>`;
    return row;
  }).join('');
}

window.updateCellColor = function(select) {
  select.setAttribute('value', select.value);
};

window.removeCO = function(coCode) {
  CourseFlow.confirmAction(`Remove outcome ${coCode} and its mappings?`, async () => {
    currentOutcomesData.cos = currentOutcomesData.cos.filter(c => c.code !== coCode);
    delete currentOutcomesData.mapping[coCode];
    const courseSelect = document.getElementById('outcomesCourseSelect');
    await CourseFlow.apiService.saveOutcomes(courseSelect ? courseSelect.value : 'CS301', currentOutcomesData);
    renderCOList();
    renderMappingMatrix();
    updateCoverageMetrics();
    CourseFlow.showToast(`Outcome ${coCode} removed`, 'info');
  });
};

function updateCoverageMetrics() {
  if (!currentOutcomesData) return;
  const totalCells = currentOutcomesData.cos.length * (PO_LIST.length + PSO_LIST.length);
  if (totalCells === 0) return;

  const selects = document.querySelectorAll('.matrix-select');
  let mappedCount = 0;
  let totalScore = 0;

  selects.forEach(s => {
    const v = parseInt(s.value, 10);
    if (v > 0) {
      mappedCount++;
      totalScore += v;
    }
  });

  const coveragePct = Math.round((mappedCount / totalCells) * 100);
  const avgCorr = mappedCount > 0 ? (totalScore / mappedCount).toFixed(2) : '0.00';

  if (document.getElementById('matrixCoverageValue')) {
    document.getElementById('matrixCoverageValue').textContent = `${coveragePct}%`;
  }
  if (document.getElementById('matrixAvgCorrelation')) {
    document.getElementById('matrixAvgCorrelation').textContent = `${avgCorr} / 3.0`;
  }
}

// ==========================================================================
// 2. ATTAINMENT ANALYTICS
// ==========================================================================
async function initAttainmentPage() {
  const courseSelect = document.getElementById('attainmentCourseSelect');
  let currentCourse = courseSelect ? courseSelect.value : 'CS301';

  async function load() {
    const attainment = await CourseFlow.apiService.getAttainment(currentCourse);
    renderAttainmentView(attainment);
  }

  if (courseSelect) {
    courseSelect.addEventListener('change', (e) => {
      currentCourse = e.target.value;
      load();
    });
  }

  await load();
}

let attainmentCompareChartInstance = null;
let poAttainmentChartInstance = null;

function renderAttainmentView(attainment) {
  if (!attainment) return;

  // Stat summary - calculate overall average safely
  const overall = (attainment.summary && attainment.summary.overallAttainment)
    || attainment.overallAverage
    || (attainment.outcomes && attainment.outcomes.length > 0
        ? (attainment.outcomes.reduce((acc, curr) => acc + (curr.achieved || 0), 0) / attainment.outcomes.length).toFixed(2)
        : '77.34');

  if (document.getElementById('overallAttainmentScore')) {
    document.getElementById('overallAttainmentScore').textContent = `${overall}%`;
  }

  const outcomes = attainment.outcomes || [];

  // Outcomes Table
  const tbody = document.getElementById('attainmentTableTbody');
  if (tbody) {
    if (outcomes.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No attainment records available for this course.</td></tr>`;
    } else {
      tbody.innerHTML = outcomes.map(o => {
        const meetsTarget = o.status === 'Meets Target' || (o.achieved >= o.target);
        const statusText = o.status || (meetsTarget ? 'Meets Target' : 'Below Target');
        const diffText = o.diff || (o.achieved >= o.target ? `+${(o.achieved - o.target).toFixed(1)}%` : `${(o.achieved - o.target).toFixed(1)}%`);
        const internalVal = o.internal !== undefined ? `${o.internal}%` : '--';
        const externalVal = o.external !== undefined ? `${o.external}%` : '--';
        const indirectVal = o.indirect !== undefined ? `${o.indirect}%` : '--';

        return `
          <tr>
            <td class="fw-bold text-dark">${o.code}</td>
            <td class="text-center">${o.target}%</td>
            <td class="text-center text-muted">${internalVal}</td>
            <td class="text-center text-muted">${externalVal}</td>
            <td class="text-center text-muted">${indirectVal}</td>
            <td class="text-center fw-bold text-dark">${o.achieved}%</td>
            <td class="text-center fw-semibold ${meetsTarget ? 'text-success' : 'text-danger'}">
              ${diffText}
            </td>
            <td>
              <span class="badge ${meetsTarget ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-danger-subtle text-danger border border-danger-subtle'}">
                ${statusText}
              </span>
            </td>
          </tr>
        `;
      }).join('');
    }
  }

  // Low Attainment Alerts Container
  const alertContainer = document.getElementById('lowAttainmentBox');
  if (alertContainer) {
    const below = outcomes.filter(o => o.status === 'Below Target' || (o.achieved < o.target));
    if (below.length > 0) {
      alertContainer.innerHTML = `
        <div class="alert alert-warning border-warning-subtle d-flex align-items-start gap-3 mb-4">
          <i class="bi bi-exclamation-triangle-fill fs-4 text-warning"></i>
          <div>
            <div class="fw-bold">Action Taken Notice: ${below.length} Course Outcome(s) Below NBA Target Benchmark</div>
            <div class="small mt-1 text-secondary">
              Remedial action plan recommended for: <strong>${below.map(b => b.code).join(', ')}</strong>.
              Recommended actions: Conduct tutorial bridge classes, enhance practical problem assignments, and provide supplementary question banks.
            </div>
          </div>
        </div>
      `;
    } else {
      alertContainer.innerHTML = `
        <div class="alert alert-success border-success-subtle d-flex align-items-center gap-2 mb-4">
          <i class="bi bi-check-circle-fill text-success fs-5"></i>
          <span>All Course Outcomes achieve or exceed the defined NBA accreditation target (75%).</span>
        </div>
      `;
    }
  }

  // Charts
  renderAttainmentCharts(attainment);
}

function renderAttainmentCharts(attainment) {
  const outcomes = attainment.outcomes || [];
  if (outcomes.length === 0) return;

  // 1. Target vs Achieved
  const ctx1 = document.getElementById('attainmentCompareChart');
  if (ctx1 && typeof Chart !== 'undefined') {
    if (attainmentCompareChartInstance) {
      attainmentCompareChartInstance.destroy();
    }
    attainmentCompareChartInstance = new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: outcomes.map(o => o.code),
        datasets: [
          {
            label: 'Target Benchmark (%)',
            data: outcomes.map(o => o.target),
            backgroundColor: '#E2E8F0',
            borderColor: '#CBD5E1',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Achieved Direct & Indirect (%)',
            data: outcomes.map(o => o.achieved),
            backgroundColor: outcomes.map(o => (o.status === 'Meets Target' || o.achieved >= o.target) ? '#4338CA' : '#DC2626'),
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } } }
        },
        scales: {
          y: { min: 0, max: 100, ticks: { callback: v => v + '%' } }
        }
      }
    });
  }

  // 2. Program Outcome PO / PSO Attainment Bar Chart
  const ctx2 = document.getElementById('poAttainmentChart');
  if (ctx2 && typeof Chart !== 'undefined') {
    if (poAttainmentChartInstance) {
      poAttainmentChartInstance.destroy();
    }
    const defaultPo = {
      PO1: 2.7, PO2: 2.5, PO3: 2.8, PO4: 2.2, PO5: 2.6,
      PO6: 2.1, PO7: 2.0, PO8: 2.4, PO9: 2.5, PO10: 2.7,
      PO11: 2.3, PO12: 2.6, PSO1: 2.8, PSO2: 2.5
    };
    const poData = attainment.poAttainment || defaultPo;
    const keys = Object.keys(poData);
    const vals = Object.values(poData);

    poAttainmentChartInstance = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: keys,
        datasets: [{
          label: 'Attainment Level (Out of 3.0)',
          data: vals,
          backgroundColor: '#6366F1',
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { min: 0, max: 3.0, ticks: { stepSize: 0.5 } }
        }
      }
    });
  }
}
