/**
 * CourseFlow - AI Handout Summarization Assistant
 * Powered by Google Gemini API
 */

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('aiAssistantRoot')) return;

  const dropzone = document.getElementById('handoutDropzone');
  const fileInput = document.getElementById('handoutFileInput');
  const processBtn = document.getElementById('startSummarizeBtn');
  const progressBox = document.getElementById('aiProcessingProgress');
  const resultsBox = document.getElementById('aiResultContainer');
  const courseSelect = document.getElementById('aiCourseSelect');

  let selectedFile = null;
  let lastAnalysisResult = null;

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function handleFileSelect(file) {
    if (!file) return;

    // Supported formats: PDF and DOCX
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      CourseFlow.showToast(
        `Unsupported file type (.${ext}). Please upload an official PDF or DOCX course handout document.`,
        'danger',
        'Invalid File Format'
      );
      return;
    }

    // Check size limit: 10MB
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      CourseFlow.showToast(
        'File size exceeds 10MB limit. Please upload a smaller document.',
        'danger',
        'File Too Large'
      );
      return;
    }

    // Check empty file
    if (file.size === 0) {
      CourseFlow.showToast(
        'The selected file is empty (0 bytes). Please upload a valid course handout.',
        'danger',
        'Empty Document'
      );
      return;
    }

    selectedFile = file;

    // Update UI Preview Bar
    document.getElementById('selectedFileName').textContent = file.name;
    const formattedSize = file.size > 1024 * 1024
      ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
      : `${(file.size / 1024).toFixed(1)} KB`;
    document.getElementById('selectedFileSize').textContent = formattedSize;

    const iconEl = document.getElementById('selectedFileIcon');
    if (iconEl) {
      if (ext === 'pdf') {
        iconEl.className = 'bi bi-file-earmark-pdf-fill fs-3 text-danger';
      } else {
        iconEl.className = 'bi bi-file-earmark-word-fill fs-3 text-primary';
      }
    }

    document.getElementById('fileSelectionCard').style.display = 'flex';
    if (processBtn) processBtn.disabled = false;
  }

  // Setup drag and drop
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  // M7-TC01: Load Sample Handout button
  const sampleBtn = document.getElementById('loadSampleHandoutBtn');
  if (sampleBtn) {
    sampleBtn.addEventListener('click', async () => {
      try {
        const response = await fetch('/static/sample_docs/CS301_Software_Engineering_Handout.pdf');
        if (!response.ok) {
          throw new Error('Sample handout document file not found on server.');
        }
        const blob = await response.blob();
        const sampleFile = new File([blob], 'CS301_Software_Engineering_Handout.pdf', { type: 'application/pdf' });
        handleFileSelect(sampleFile);
        CourseFlow.showToast('Sample course handout loaded (PDF). Click "Generate Summary with Gemini" to begin.', 'info', 'Handout Loaded');
      } catch (err) {
        CourseFlow.showToast('Failed to load sample handout: ' + err.message, 'danger', 'Error');
      }
    });
  }

  // Remove file button
  const removeFileBtn = document.getElementById('removeFileBtn');
  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', () => {
      selectedFile = null;
      lastAnalysisResult = null;
      if (fileInput) fileInput.value = '';
      document.getElementById('fileSelectionCard').style.display = 'none';
      if (processBtn) processBtn.disabled = true;
      if (resultsBox) resultsBox.style.display = 'none';
    });
  }

  // M7-TC03: Start Summarization with Google Gemini
  if (processBtn) {
    processBtn.addEventListener('click', async () => {
      if (!selectedFile) {
        CourseFlow.showToast('Please select or upload a course handout document first.', 'warning', 'No File Selected');
        return;
      }

      const courseId = courseSelect ? courseSelect.value : 'CS301';

      // UI state: loading
      processBtn.disabled = true;
      if (progressBox) progressBox.style.display = 'block';
      if (resultsBox) resultsBox.style.display = 'none';

      const progressLabel = document.getElementById('aiProgressLabel');
      if (progressLabel) {
        progressLabel.textContent = `Analyzing ${selectedFile.name} with Google Gemini AI...`;
      }

      // Build FormData with real file
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('courseId', courseId);

      try {
        const result = await CourseFlow.apiService.summarizeHandout(formData);
        lastAnalysisResult = result;

        if (progressBox) progressBox.style.display = 'none';
        if (resultsBox) resultsBox.style.display = 'block';
        processBtn.disabled = false;

        populateAiResults(result);
        CourseFlow.showToast('Handout analyzed and structured summary generated by Gemini AI!', 'success', 'Analysis Succeeded');
      } catch (err) {
        if (progressBox) progressBox.style.display = 'none';
        processBtn.disabled = false;
        // Never substitute fake predefined results when API fails
        CourseFlow.showToast(err.message || 'Gemini document analysis failed.', 'danger', 'Generation Failed');
      }
    });
  }

  // M7-TC04: Faculty Verification & Save into Official Syllabus
  const approveBtn = document.getElementById('approveAiSummaryBtn');
  if (approveBtn) {
    approveBtn.addEventListener('click', async () => {
      if (!lastAnalysisResult) {
        CourseFlow.showToast('No active Gemini analysis results to approve.', 'warning');
        return;
      }

      const courseId = courseSelect ? courseSelect.value : (lastAnalysisResult.courseCode || 'CS301');
      const editedSummary = document.getElementById('aiSummaryTextArea')
        ? document.getElementById('aiSummaryTextArea').value
        : lastAnalysisResult.extractedSummary;

      CourseFlow.confirmAction(
        `Faculty Review Confirmation:\n\nDo you confirm that you have reviewed the extracted course summary, topics, and outcomes, and approve saving them into the official syllabus for ${courseId}?`,
        async () => {
          try {
            // Build syllabus units from extracted data
            const info = lastAnalysisResult.importantInformation || {};
            const unitNames = info.unitNames || [];
            const cos = lastAnalysisResult.suggestedOutcomesDetailed || [];
            const topics = lastAnalysisResult.topicsIdentified || [];

            let newUnits = [];

            if (unitNames.length > 0) {
              unitNames.forEach((uTitle, idx) => {
                const uNo = idx + 1;
                const coItem = cos[idx] || cos[0] || { co: `CO${uNo}` };
                const uTopics = (coItem.relevantTopics && coItem.relevantTopics.length > 0)
                  ? coItem.relevantTopics.join(', ')
                  : (topics.slice(idx * 2, idx * 2 + 2).join(', ') || 'Curriculum fundamentals and applications.');

                newUnits.push({
                  unit: uNo,
                  title: uTitle.replace(/^Unit\s*\d+\s*[:\-]\s*/i, '').trim(),
                  hours: 9,
                  outcomes: coItem.co || `CO${uNo}`,
                  topics: uTopics
                });
              });
            } else if (cos.length > 0) {
              cos.forEach((coItem, idx) => {
                const uNo = idx + 1;
                newUnits.push({
                  unit: uNo,
                  title: coItem.statement.length > 45 ? `${coItem.statement.substring(0, 42)}...` : coItem.statement,
                  hours: 9,
                  outcomes: coItem.co || `CO${uNo}`,
                  topics: Array.isArray(coItem.relevantTopics) && coItem.relevantTopics.length > 0
                    ? coItem.relevantTopics.join(', ')
                    : topics.join(', ')
                });
              });
            } else {
              newUnits.push({
                unit: 1,
                title: lastAnalysisResult.courseTitle || 'Course Core Modules',
                hours: 45,
                outcomes: 'CO1, CO2, CO3',
                topics: topics.join(', ')
              });
            }

            // 1. Save in local CourseFlow DB store
            await CourseFlow.apiService.saveSyllabus(courseId, newUnits);

            // 2. Save in backend REST API endpoint
            try {
              await fetch(`/api/syllabus/${courseId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ units: newUnits })
              });
            } catch (netErr) {
              console.warn('Backend syllabus sync warning:', netErr);
            }

            CourseFlow.showToast(
              `Syllabus updated successfully for ${courseId} with ${newUnits.length} verified units! You can inspect them in the Syllabus module.`,
              'success',
              'Syllabus Saved'
            );
          } catch (saveErr) {
            CourseFlow.showToast('Failed to save syllabus: ' + saveErr.message, 'danger', 'Save Error');
          }
        },
        'Approve & Save into Syllabus'
      );
    });
  }

  function populateAiResults(data) {
    // Document Badge
    const docBadge = document.getElementById('aiDocumentBadge');
    if (docBadge) {
      docBadge.textContent = `Document: ${data.fileName || 'Course_Handout'} | Course: ${data.courseCode || 'CS301'} - ${data.courseTitle || 'Software Engineering'}`;
    }

    const targetCourseLabel = document.getElementById('approvalTargetCourseCode');
    if (targetCourseLabel) {
      targetCourseLabel.textContent = data.courseCode || (courseSelect ? courseSelect.value : 'CS301');
    }

    // Section A: Executive Course Summary
    const summaryArea = document.getElementById('aiSummaryTextArea');
    if (summaryArea) {
      summaryArea.value = data.extractedSummary || '';
    }

    // Section B: Key Topics
    const topicsList = document.getElementById('aiExtractedTopicsList');
    if (topicsList) {
      const topics = data.topicsIdentified || [];
      if (topics.length === 0) {
        topicsList.innerHTML = `<li class="list-group-item text-muted small py-2">No key topics found in document.</li>`;
      } else {
        topicsList.innerHTML = topics.map(t => `
          <li class="list-group-item d-flex align-items-center gap-2 py-2 small">
            <i class="bi bi-check2-circle text-primary"></i>
            <span>${escapeHtml(t)}</span>
          </li>
        `).join('');
      }
    }

    // Section C: Suggested Course Outcomes
    const loList = document.getElementById('aiSuggestedLOList');
    if (loList) {
      const cos = data.suggestedOutcomesDetailed || [];
      if (cos.length === 0 && data.suggestedOutcomes && data.suggestedOutcomes.length > 0) {
        loList.innerHTML = data.suggestedOutcomes.map(lo => `
          <div class="p-2 border rounded bg-light mb-2 small text-dark">
            <strong class="text-primary me-1">${escapeHtml(lo.split(':')[0])}:</strong> ${escapeHtml(lo.split(':')[1] || lo)}
          </div>
        `).join('');
      } else if (cos.length === 0) {
        loList.innerHTML = `<div class="p-2 text-muted small">No Course Outcomes suggested from document.</div>`;
      } else {
        loList.innerHTML = cos.map(co => {
          const coId = co.co || 'CO';
          const statement = co.statement || '';
          const supportingTopics = Array.isArray(co.relevantTopics) && co.relevantTopics.length > 0
            ? `<div class="mt-2 text-muted" style="font-size:0.75rem;">
                 <strong>Supporting Topics:</strong>
                 <div class="mt-1 d-flex flex-wrap gap-1">
                   ${co.relevantTopics.map(r => `<span class="badge bg-white text-dark border">${escapeHtml(r)}</span>`).join('')}
                 </div>
               </div>`
            : '';

          return `
            <div class="p-3 border rounded bg-light mb-2 small text-dark">
              <div class="d-flex align-items-start gap-2">
                <span class="badge bg-primary fw-bold mt-1">${escapeHtml(coId)}</span>
                <div class="flex-grow-1">
                  <div class="fw-semibold text-dark">${escapeHtml(statement)}</div>
                  ${supportingTopics}
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    // Section D: Important Information & Extracted Units
    const importantBox = document.getElementById('aiImportantInfoBox');
    if (importantBox) {
      const info = data.importantInformation || {};
      let html = '';

      if (info.unitNames && info.unitNames.length > 0) {
        html += `
          <div class="mb-3">
            <div class="fw-bold small text-dark mb-1">
              <i class="bi bi-collection me-1 text-primary"></i> Extracted Syllabus Units (${info.unitNames.length}):
            </div>
            <ul class="mb-0 ps-3 small text-secondary">
              ${info.unitNames.map(u => `<li>${escapeHtml(u)}</li>`).join('')}
            </ul>
          </div>
        `;
      }

      if (info.learningObjectives && info.learningObjectives.length > 0) {
        html += `
          <div class="mb-3">
            <div class="fw-bold small text-dark mb-1">
              <i class="bi bi-card-checklist me-1 text-success"></i> Course Learning Objectives:
            </div>
            <ul class="mb-0 ps-3 small text-secondary">
              ${info.learningObjectives.map(o => `<li>${escapeHtml(o)}</li>`).join('')}
            </ul>
          </div>
        `;
      }

      if (info.importantConcepts && info.importantConcepts.length > 0) {
        html += `
          <div>
            <div class="fw-bold small text-dark mb-1">
              <i class="bi bi-lightbulb me-1 text-warning"></i> Core Concepts:
            </div>
            <div class="d-flex flex-wrap gap-1">
              ${info.importantConcepts.map(c => `<span class="badge bg-white text-secondary border">${escapeHtml(c)}</span>`).join('')}
            </div>
          </div>
        `;
      }

      if (!html) {
        html = `
          <div class="small text-muted">
            <i class="bi bi-check-circle text-success me-1"></i> Course title: <strong>${escapeHtml(data.courseTitle || 'Software Engineering')}</strong> (${escapeHtml(data.courseCode || 'CS301')}).
          </div>
        `;
      }

      importantBox.innerHTML = html;
    }
  }
});
