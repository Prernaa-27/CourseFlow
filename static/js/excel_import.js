/**
 * CourseFlow - Generic Excel Import Engine Controller
 * Manages workbook inspection, worksheet selection, dynamic column mapping,
 * data preview, validation, transactional database execution, and error reporting.
 */

document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('excelImportFileInput');
  const sheetSelect = document.getElementById('excelSheetSelect');
  const previewContainer = document.getElementById('excelPreviewContainer');
  const executeBtn = document.getElementById('executeImportBtn');
  const resultContainer = document.getElementById('excelImportResultContainer');

  let currentFile = null;
  let currentInspection = null;
  let currentPreview = null;
  let currentCourseId = localStorage.getItem('cf_selected_course') || 'CSE2724';

  if (!fileInput) return;

  // 1. File Selected -> Inspect Workbook
  fileInput.addEventListener('change', async (e) => {
    if (!e.target.files.length) return;
    currentFile = e.target.files[0];
    const formData = new FormData();
    formData.append('file', currentFile);

    document.getElementById('excelInspectSpinner').classList.remove('d-none');
    document.getElementById('excelStepSheetSelect').classList.add('d-none');
    previewContainer.classList.add('d-none');
    resultContainer.classList.add('d-none');

    try {
      const res = await fetch('/api/import/inspect', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      document.getElementById('excelInspectSpinner').classList.add('d-none');

      if (!data.success) {
        CourseFlow.showToast(data.error || 'Failed to inspect Excel workbook', 'danger', 'Excel Error');
        return;
      }

      currentInspection = data;
      sheetSelect.innerHTML = data.sheets.map(s => `
        <option value="${s.name}">${s.name} (${s.maxRows} rows, ${s.maxCols} cols)</option>
      `).join('');

      // Auto-select 'Clean Maitri Data' or first sheet
      const bestSheet = data.sheets.find(s => s.name.toLowerCase().includes('clean') || s.name.toLowerCase().includes('data')) || data.sheets[0];
      sheetSelect.value = bestSheet.name;

      document.getElementById('excelStepSheetSelect').classList.remove('d-none');
      await loadSheetPreview(bestSheet.name);
    } catch (err) {
      document.getElementById('excelInspectSpinner').classList.add('d-none');
      CourseFlow.showToast(err.message || 'Error uploading file', 'danger');
    }
  });

  // 2. Sheet Changed
  sheetSelect.addEventListener('change', async () => {
    await loadSheetPreview(sheetSelect.value);
  });

  async function loadSheetPreview(sheetName) {
    if (!currentFile) return;
    const headerRow = parseInt(document.getElementById('excelHeaderRowInput')?.value || '10', 10);
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('sheetName', sheetName);
    formData.append('headerRow', headerRow);

    document.getElementById('excelPreviewSpinner').classList.remove('d-none');
    previewContainer.classList.add('d-none');

    try {
      const res = await fetch('/api/import/preview', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      document.getElementById('excelPreviewSpinner').classList.add('d-none');

      if (!data.success) {
        CourseFlow.showToast(data.error || 'Failed to preview sheet', 'warning');
        return;
      }

      currentPreview = data;
      renderMappingControls(data.headers);
      renderPreviewTable(data.headers, data.previewRows);
      previewContainer.classList.remove('d-none');
      executeBtn.disabled = false;
    } catch (err) {
      document.getElementById('excelPreviewSpinner').classList.add('d-none');
      CourseFlow.showToast('Preview error: ' + err.message, 'danger');
    }
  }

  // 3. Render Column Mapping Selectors
  async function renderMappingControls(headers) {
    const rollSelect = document.getElementById('mapColRoll');
    const nameSelect = document.getElementById('mapColName');
    const asmContainer = document.getElementById('mapColAssessmentsContainer');

    const optionsHtml = headers.map(h => `
      <option value="${h.colIndex}">${h.colLetter}: ${h.header}</option>
    `).join('');

    rollSelect.innerHTML = optionsHtml;
    nameSelect.innerHTML = optionsHtml;

    // Auto-guess Roll No and Name
    const rollH = headers.find(h => h.header.toLowerCase().includes('roll') || h.header.toLowerCase().includes('id'));
    if (rollH) rollSelect.value = rollH.colIndex;
    const nameH = headers.find(h => h.header.toLowerCase().includes('name') || h.header.toLowerCase().includes('student'));
    if (nameH) nameSelect.value = nameH.colIndex;

    // Fetch Course Assessments to map
    try {
      const cId = localStorage.getItem('cf_selected_course') || 'CSE2724';
      const asmRes = await fetch(`/api/records/${cId}/marks`);
      const asmData = await asmRes.json();
      const asms = asmData.assessments || [];

      asmContainer.innerHTML = asms.map(a => {
        // Auto-guess matching column
        const matchedCol = headers.find(h => {
          const htxt = h.header.toLowerCase();
          const atxt = a.name.toLowerCase();
          return (atxt.includes('lab') && htxt.includes('lab')) ||
                 (atxt.includes('proj') && htxt.includes('proj')) ||
                 ((atxt.includes('end') || atxt.includes('term')) && (htxt.includes('end') || htxt.includes('term')));
        });

        return `
          <div class="col-md-6 mb-2">
            <label class="small text-muted fw-semibold mb-1">${a.name} (Max ${a.maxMarks}):</label>
            <select class="form-select form-select-sm map-asm-select" data-asm-id="${a.id}">
              <option value="">-- Do Not Import --</option>
              ${headers.map(h => `
                <option value="${h.colIndex}" ${matchedCol && matchedCol.colIndex === h.colIndex ? 'selected' : ''}>
                  ${h.colLetter}: ${h.header}
                </option>
              `).join('')}
            </select>
          </div>
        `;
      }).join('');
    } catch (e) {
      console.warn('Could not load course assessments for mapping', e);
    }
  }

  // 4. Render Preview Rows
  function renderPreviewTable(headers, rows) {
    const thead = document.getElementById('excelPreviewThead');
    const tbody = document.getElementById('excelPreviewTbody');

    thead.innerHTML = `<tr>${headers.map(h => `<th>${h.colLetter}: ${h.header}</th>`).join('')}</tr>`;
    if (!rows || rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="${headers.length}" class="text-center text-muted py-3">No preview records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = rows.map(r => `
      <tr>${headers.map(h => `<td class="small">${r[h.header] !== undefined ? r[h.header] : ''}</td>`).join('')}</tr>
    `).join('');
  }

  // 5. Execute Import Button
  executeBtn.addEventListener('click', async () => {
    if (!currentFile || !currentPreview) return;

    executeBtn.disabled = true;
    executeBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Importing...`;

    const rollCol = document.getElementById('mapColRoll').value;
    const nameCol = document.getElementById('mapColName').value;
    const asmSelects = document.querySelectorAll('.map-asm-select');
    const asmMap = {};
    asmSelects.forEach(s => {
      if (s.value) asmMap[s.dataset.asmId] = s.value;
    });

    const mapping = {
      roll_no: rollCol,
      name: nameCol,
      assessments: asmMap
    };

    const headerRow = parseInt(document.getElementById('excelHeaderRowInput')?.value || '10', 10);
    const dataStartRow = currentPreview.dataStartRow || 12;
    const overwrite = document.getElementById('excelOverwriteCheckbox')?.checked || false;
    const courseId = localStorage.getItem('cf_selected_course') || 'CSE2724';

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('sheetName', sheetSelect.value);
    formData.append('courseId', courseId);
    formData.append('headerRow', headerRow);
    formData.append('dataStartRow', dataStartRow);
    formData.append('overwrite', overwrite);
    formData.append('columnMapping', JSON.stringify(mapping));

    try {
      const res = await fetch('/api/import/execute', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      executeBtn.disabled = false;
      executeBtn.innerHTML = `<i class="bi bi-cloud-arrow-up me-1"></i> Confirm & Import to Database`;

      if (!data.success) {
        CourseFlow.showToast(data.error || 'Import failed', 'danger', 'Import Error');
        return;
      }

      // Render Results Summary
      renderImportSummary(data);
      CourseFlow.showToast(`Import completed: ${data.importedCount} records saved to database!`, 'success', 'Import Success');
    } catch (err) {
      executeBtn.disabled = false;
      executeBtn.innerHTML = `<i class="bi bi-cloud-arrow-up me-1"></i> Confirm & Import to Database`;
      CourseFlow.showToast(err.message || 'Server error during import', 'danger');
    }
  });

  function renderImportSummary(data) {
    resultContainer.classList.remove('d-none');
    document.getElementById('summaryImportedCount').textContent = data.importedCount;
    document.getElementById('summarySkippedCount').textContent = data.skippedCount;
    document.getElementById('summaryRejectedCount').textContent = data.rejectedCount;

    const errorBtn = document.getElementById('downloadErrorReportBtn');
    if (data.errorReport && data.errorReport.length > 0) {
      errorBtn.classList.remove('d-none');
      errorBtn.onclick = () => downloadErrorReportCsv(data.errorReport);
    } else {
      errorBtn.classList.add('d-none');
    }
  }

  function downloadErrorReportCsv(report) {
    let csv = "Row,Roll No,Student Name,Error Description\n";
    report.forEach(r => {
      const cleanErr = (r.error || '').replace(/"/g, '""');
      csv += `${r.row},"${r.roll}","${r.name}","${cleanErr}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `CourseFlow_Import_Error_Report_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  }
});
