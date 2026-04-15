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

const ANALYZE_API = '/resume/analyze';
const CIRCLE_RADIUS = 52;
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS;

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
  if (!items || !items.length) {
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
  updateProgress(data.score || 0);
  resultTitle.textContent = 'Resume performance';
  resultSummary.textContent = 'Here are your resume strengths, weaknesses, and missing skills.';
  displayItems(strengthsList, data.strengths);
  displayItems(weaknessesList, data.weaknesses);
  displayItems(missingSkillsList, data.missing_skills);
}

function resetForm() {
  fileInput.value = '';
  textInput.value = '';
  linkInput.value = '';
  scoreValue.textContent = '0%';
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

function collectFormData() {
  const formData = new FormData();
  const file = fileInput.files[0];
  const text = textInput.value.trim();
  const link = linkInput.value.trim();

  if (file) {
    formData.append('file', file);
  }
  if (text) {
    formData.append('text', text);
  }
  if (link) {
    formData.append('profileLink', link);
  }

  return formData;
}

async function analyzeResume() {
  const file = fileInput.files[0];
  const text = textInput.value.trim();
  const link = linkInput.value.trim();

  if (!file && !text && !link) {
    alert('Please upload a file, paste resume text, or provide a profile link.');
    return;
  }

  const formData = collectFormData();
  setLoading(true);
  analyzeButton.disabled = true;
  analyzeButton.textContent = 'Analyzing...';

  try {
    const response = await fetch(ANALYZE_API, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Resume analysis failed.');
    }

    const result = await response.json();
    showResult(result);
  } catch (error) {
    resultTitle.textContent = 'Analysis error';
    resultSummary.textContent = error.message || 'Unable to analyze your resume at this time.';
    strengthsList.innerHTML = '<li class="empty-item">Unable to load strengths</li>';
    weaknessesList.innerHTML = '<li class="empty-item">Unable to load weaknesses</li>';
    missingSkillsList.innerHTML = '<li class="empty-item">Unable to load missing skills</li>';
  } finally {
    setLoading(false);
    analyzeButton.disabled = false;
    analyzeButton.textContent = 'Analyze resume';
  }
}

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

setLoading(false);
updateProgress(0);
