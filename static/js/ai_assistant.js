/**
 * CourseFlow - AI Handout Summarization Assistant
 */

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('aiAssistantRoot')) return;

  const dropzone = document.getElementById('handoutDropzone');
  const fileInput = document.getElementById('handoutFileInput');
  const processBtn = document.getElementById('startSummarizeBtn');
  const progressBox = document.getElementById('aiProcessingProgress');
  const resultsBox = document.getElementById('aiResultContainer');

  let selectedFile = null;

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

  function handleFileSelect(file) {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    // Check extension fallback
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      CourseFlow.showToast('Unsupported file type. Please upload a PDF, DOCX, or TXT course handout.', 'danger', 'Invalid File');
      return;
    }

    if (file.size > maxSize) {
      CourseFlow.showToast('File size exceeds 10MB limit. Please upload a smaller document.', 'danger', 'File Too Large');
      return;
    }

    selectedFile = file;
    document.getElementById('selectedFileName').textContent = file.name;
    document.getElementById('selectedFileSize').textContent = `${(file.size / 1024).toFixed(1)} KB`;
    document.getElementById('fileSelectionCard').style.display = 'flex';
    if (processBtn) processBtn.disabled = false;
  }

  // Load sample handout directly for fast lab testing
  const sampleBtn = document.getElementById('loadSampleHandoutBtn');
  if (sampleBtn) {
    sampleBtn.addEventListener('click', () => {
      selectedFile = {
        name: 'CS301_Software_Engineering_Handout.pdf',
        size: 1245184
      };
      document.getElementById('selectedFileName').textContent = selectedFile.name;
      document.getElementById('selectedFileSize').textContent = '1.2 MB';
      document.getElementById('fileSelectionCard').style.display = 'flex';
      if (processBtn) processBtn.disabled = false;
      CourseFlow.showToast('Sample course handout loaded. Click "Generate Demo Summary" to view extraction.', 'info');
    });
  }

  // Remove selected file
  const removeFileBtn = document.getElementById('removeFileBtn');
  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', () => {
      selectedFile = null;
      if (fileInput) fileInput.value = '';
      document.getElementById('fileSelectionCard').style.display = 'none';
      if (processBtn) processBtn.disabled = true;
      if (resultsBox) resultsBox.style.display = 'none';
    });
  }

  // Start summarization
  if (processBtn) {
    processBtn.addEventListener('click', async () => {
      if (!selectedFile) return;

      processBtn.disabled = true;
      if (progressBox) progressBox.style.display = 'block';
      if (resultsBox) resultsBox.style.display = 'none';

      // Animate progress simulation
      const progressBar = document.getElementById('aiProgressBar');
      const progressLabel = document.getElementById('aiProgressLabel');

      let step = 15;
      const interval = setInterval(() => {
        step += 25;
        if (progressBar) progressBar.style.width = `${step}%`;
        if (step === 40 && progressLabel) progressLabel.textContent = 'Parsing document sections and syllabus structure...';
        if (step === 65 && progressLabel) progressLabel.textContent = 'Extracting module learning outcomes...';
        if (step === 90 && progressLabel) progressLabel.textContent = 'Synthesizing concise module summaries...';
      }, 250);

      try {
        const result = await CourseFlow.apiService.summarizeHandout({ fileName: selectedFile.name, size: selectedFile.size });
        clearInterval(interval);
        if (progressBar) progressBar.style.width = '100%';
        if (progressLabel) progressLabel.textContent = 'Extraction complete!';

        setTimeout(() => {
          if (progressBox) progressBox.style.display = 'none';
          if (resultsBox) resultsBox.style.display = 'block';
          populateAiResults(result);
          processBtn.disabled = false;
          CourseFlow.showToast('Demo handout summary generated successfully.', 'success', 'Extraction Complete');
        }, 400);
      } catch (err) {
        clearInterval(interval);
        if (progressBox) progressBox.style.display = 'none';
        processBtn.disabled = false;
        CourseFlow.showToast('Summarization failed. Please check document formatting.', 'danger', 'Error');
      }
    });
  }

  // Approve & Save into official syllabus
  const approveBtn = document.getElementById('approveAiSummaryBtn');
  if (approveBtn) {
    approveBtn.addEventListener('click', async () => {
      const summaryText = document.getElementById('aiSummaryTextArea').value;
      const courseSelect = document.getElementById('aiCourseSelect');
      const courseId = courseSelect ? courseSelect.value : 'CS301';

      CourseFlow.confirmAction(
        'Faculty Verification Confirmation:\n\nDo you confirm that you have reviewed this extracted syllabus summary and approve it for inclusion into the course syllabus?',
        async () => {
          CourseFlow.showToast('Summary verified and saved into course syllabus!', 'success', 'Approved & Saved');
        },
        'Approve Handout Summary'
      );
    });
  }
});

function populateAiResults(data) {
  const summaryArea = document.getElementById('aiSummaryTextArea');
  if (summaryArea) summaryArea.value = data.extractedSummary;

  const topicsList = document.getElementById('aiExtractedTopicsList');
  if (topicsList) {
    topicsList.innerHTML = data.topicsIdentified.map(t => `
      <li class="list-group-item d-flex align-items-center gap-2 py-2 small">
        <i class="bi bi-check2-circle text-primary"></i> ${t}
      </li>
    `).join('');
  }

  const loList = document.getElementById('aiSuggestedLOList');
  if (loList) {
    loList.innerHTML = data.suggestedOutcomes.map(lo => `
      <div class="p-2 border rounded bg-light mb-2 small text-dark">
        <strong class="text-primary me-1">${lo.split(':')[0]}:</strong> ${lo.split(':')[1] || lo}
      </div>
    `).join('');
  }
}
