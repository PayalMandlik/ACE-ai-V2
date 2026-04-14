const QUESTIONS_API = '/assessment';
const SUBMIT_API = '/assessment/submit';

const questionTitle = document.getElementById('question-title');
const questionText = document.getElementById('question-text');
const answerInput = document.getElementById('answer-input');
const questionProgress = document.getElementById('question-progress');
const summaryCount = document.getElementById('summary-count');
const summaryStreak = document.getElementById('summary-streak');
const resultScore = document.getElementById('result-score');
const resultXp = document.getElementById('result-xp');
const resultFeedback = document.getElementById('result-feedback');
const prevButton = document.getElementById('prev-question');
const nextButton = document.getElementById('next-question');
const submitButton = document.getElementById('submit-assessment');
const timerElement = document.getElementById('assessment-timer');

let questions = [];
let assessmentId = null;
let currentIndex = 0;
let answers = {};
let timerSeconds = 900;
let timerInterval;

function formatTime(seconds) {
  const minutes = String(Math.floor(seconds / 60)).padStart(2, '0');
  const secs = String(seconds % 60).padStart(2, '0');
  return `${minutes}:${secs}`;
}

function setTimer(seconds) {
  timerSeconds = seconds;
  timerElement.textContent = formatTime(timerSeconds);
}

function startTimer() {
  timerInterval = setInterval(() => {
    timerSeconds -= 1;
    timerElement.textContent = formatTime(timerSeconds);
    if (timerSeconds <= 0) {
      clearInterval(timerInterval);
      submitAssessment();
    }
  }, 1000);
}

function updateProgress() {
  const percentage = questions.length ? ((currentIndex + 1) / questions.length) * 100 : 0;
  questionProgress.style.width = `${percentage}%`;
  summaryCount.textContent = `${currentIndex + 1} / ${questions.length} completed`;
}

function renderQuestion() {
  const question = questions[currentIndex];
  if (!question) return;

  questionTitle.textContent = `Question ${currentIndex + 1}`;
  // FIX: backend field is `question`, not `text`
  questionText.textContent = question.question || question.text || '';
  answerInput.innerHTML = '';

  if (Array.isArray(question.options) && question.options.length) {
    question.options.forEach((option) => {
      const label = document.createElement('label');
      label.className = 'option-label';
      const radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = 'answer';
      radio.value = option;
      radio.checked = answers[question.id] === option;
      radio.addEventListener('change', () => { answers[question.id] = option; });
      label.appendChild(radio);
      label.appendChild(document.createTextNode(option));
      answerInput.appendChild(label);
    });
  } else {
    const textarea = document.createElement('textarea');
    textarea.className = 'answer-textarea';
    textarea.rows = 5;
    textarea.placeholder = 'Write your answer here...';
    textarea.value = answers[question.id] || '';
    textarea.addEventListener('input', () => { answers[question.id] = textarea.value; });
    answerInput.appendChild(textarea);
  }

  prevButton.disabled = currentIndex === 0;
  nextButton.disabled = currentIndex === questions.length - 1;
  updateProgress();
}

// FIX: GET /assessment requires ?skill= query param — prompt user first
function promptSkillAndLoad() {
  const skill = window.prompt('Enter the skill to be assessed on (e.g. Python, React, SQL):');
  if (!skill || !skill.trim()) {
    questionTitle.textContent = 'No skill provided';
    questionText.textContent = 'Reload the page and enter a skill name to start the assessment.';
    submitButton.disabled = true;
    return;
  }
  loadQuestions(skill.trim());
}

async function loadQuestions(skill) {
  questionTitle.textContent = 'Loading questions...';
  questionText.textContent = 'Please wait...';

  try {
    const response = await fetch(`${QUESTIONS_API}?skill=${encodeURIComponent(skill)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Unable to load assessment questions.');
    }

    // FIX: response is {assessment_id, skill, questions} — not a bare array
    const data = await response.json();
    assessmentId = data.assessment_id;
    questions = data.questions || [];

    if (!questions.length) throw new Error('No questions available for this skill.');

    renderQuestion();
    startTimer();
  } catch (error) {
    questionTitle.textContent = 'Quiz failed to load';
    questionText.textContent = error.message;
    submitButton.disabled = true;
  }
}

async function submitAssessment() {
  if (!questions.length) return;

  submitButton.disabled = true;
  submitButton.textContent = 'Submitting...';
  clearInterval(timerInterval);

  try {
    // FIX: payload needs assessment_id; answers as List[{id, answer}]
    const answerList = questions.map((q) => ({ id: q.id, answer: answers[q.id] || '' }));

    const response = await fetch(SUBMIT_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assessment_id: assessmentId, answers: answerList }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Submission failed.');
    }

    const result = await response.json();
    resultScore.textContent = `Score: ${result.score || 0}%`;
    resultXp.textContent = `XP gained: ${result.xp || 0}`;
    // FIX: feedback is List[str]
    const feedbackText = Array.isArray(result.feedback)
      ? result.feedback.join(' | ')
      : result.feedback || 'Review your results and improve your score next time.';
    resultFeedback.textContent = feedbackText;
    submitButton.textContent = 'Submitted';
  } catch (error) {
    resultFeedback.textContent = error.message;
    submitButton.disabled = false;
    submitButton.textContent = 'Submit answers';
  }
}

prevButton.addEventListener('click', () => {
  if (currentIndex > 0) { currentIndex -= 1; renderQuestion(); }
});

nextButton.addEventListener('click', () => {
  if (currentIndex < questions.length - 1) { currentIndex += 1; renderQuestion(); }
});

submitButton.addEventListener('click', submitAssessment);

setTimer(900);
promptSkillAndLoad();