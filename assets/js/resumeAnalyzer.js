const analyzeButton = document.getElementById('analyze-button');
const resetButton = document.getElementById('reset-analyzer');
const dropzone = document.getElementById('upload-dropzone');
const fileInput = document.getElementById('resume-file');
const textInput = document.getElementById('resume-text');
const linkInput = document.getElementById('resume-link');

const analysisPane = document.getElementById('analysis-pane');
const loadingState = document.getElementById('loading-state');
const resultsPanel = document.getElementById('analysis-results');

const scoreValue = document.getElementById('resume-score-value');
const strengthsList = document.getElementById('strengths-list');
const weaknessesList = document.getElementById('weaknesses-list');
const missingSkillsList = document.getElementById('missing-skills-list');

const resultTitle = document.getElementById('result-title');
const resultSummary = document.getElementById('result-summary');

const progressRing = document.querySelector('.progress-ring .ring-progress');

const ANALYZE_API = "http://127.0.0.1:8000/resume/analyze";

const CIRCLE_RADIUS = 52;
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS;


// ================== UI HELPERS ==================

function updateProgress(score) {
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  const offset = CIRCLE_CIRCUMFERENCE - (normalizedScore / 100) * CIRCLE_CIRCUMFERENCE;

  if (progressRing) {
    progressRing.style.strokeDasharray = `${CIRCLE_CIRCUMFERENCE} ${CIRCLE_CIRCUMFERENCE}`;
    progressRing.style.strokeDashoffset = offset;
  }

  if (scoreValue) {
    scoreValue.textContent = `${normalizedScore}%`;
  }
}

function setLoading(active) {
  loadingState.style.display = active ? 'flex' : 'none';
  resultsPanel.style.display = active ? 'none' : 'block';
}

function displayItems(container, items) {
  container.innerHTML = '';

  if (!items || items.length === 0) {
    container.innerHTML = '<li class="empty-item">No items found</li>';
    return;
  }

  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    container.appendChild(li);
  });
}

function showResult(data) {
  // supports both formats
  const analysis = data.analysis || data;

  updateProgress(analysis.score || 0);

  resultTitle.textContent = "Resume Analysis Result";
  resultSummary.textContent = "AI-powered ATS evaluation";

  displayItems(strengthsList, analysis.strengths);
  displayItems(weaknessesList, analysis.weaknesses);
  displayItems(missingSkillsList, analysis.missing_skills);
}


// ================== FORM HANDLING ==================

function resetForm() {
  fileInput.value = '';
  textInput.value = '';
  linkInput.value = '';

  dropzone.classList.remove('file-loaded');

  updateProgress(0);

  strengthsList.innerHTML = '<li class="empty-item">No items found</li>';
  weaknessesList.innerHTML = '<li class="empty-item">No items found</li>';
  missingSkillsList.innerHTML = '<li class="empty-item">No items found</li>';

  resultTitle.textContent = 'Resume performance';
  resultSummary.textContent = 'Submit your resume to see results.';
}

function highlightDropzone(active) {
  dropzone.classList.toggle('drop-active', active);
}


// ================== FORM DATA ==================

function collectFormData() {
  const formData = new FormData();

  const file = fileInput.files[0];
  const text = textInput.value.trim();

  if (file) {
    formData.append("source", "file");
    formData.append("file", file);
  } else if (text) {
    formData.append("source", "text");
    formData.append("text", text);
  }

  return formData;
}


// ================== API CALL ==================

async function analyzeResume() {
  const file = fileInput.files[0];
  const text = textInput.value.trim();

  if (!file && !text) {
    alert("Please upload a file or paste resume text.");
    return;
  }

  const formData = collectFormData();

  setLoading(true);
  analyzeButton.disabled = true;
  analyzeButton.textContent = "Analyzing...";

  try {
    const response = await fetch(ANALYZE_API, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Resume analysis failed.");
    }

    showResult(result);

  } catch (error) {
    resultTitle.textContent = "Analysis error";
    resultSummary.textContent = error.message;

    strengthsList.innerHTML = '<li class="empty-item">Error</li>';
    weaknessesList.innerHTML = '<li class="empty-item">Error</li>';
    missingSkillsList.innerHTML = '<li class="empty-item">Error</li>';
  } finally {
    setLoading(false);
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analyze resume";
  }
}


// ================== EVENTS ==================

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) {
    dropzone.classList.add('file-loaded');
  } else {
    dropzone.classList.remove('file-loaded');
  }
});

['dragenter', 'dragover'].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    highlightDropzone(true);
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (eventName === 'drop') {
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        dropzone.classList.add('file-loaded');
      }
    }

    highlightDropzone(false);
  });
});

dropzone.addEventListener('click', () => fileInput.click());

analyzeButton.addEventListener('click', analyzeResume);

resetButton.addEventListener('click', () => {
  resetForm();
  setLoading(false);
});


// ================== INIT ==================

setLoading(false);
updateProgress(0);