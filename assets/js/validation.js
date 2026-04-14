const validateButton = document.getElementById('validate-github');
const clearValidation = document.getElementById('clear-validation');
const repoInput = document.getElementById('github-repo');
const projectScore = document.getElementById('project-score');
const scoreFill = document.getElementById('score-fill');
const scoreBadge = document.getElementById('score-badge');
const projectSummary = document.getElementById('project-summary');
const projectSkills = document.getElementById('project-skills');
const projectWeaknesses = document.getElementById('project-weaknesses');

const VALIDATE_API = '/validate/github';

function updateScore(score) {
  const validatedScore = Math.max(0, Math.min(score, 100));
  projectScore.textContent = `${validatedScore}%`;
  scoreFill.style.width = `${validatedScore}%`;
  scoreBadge.textContent = validatedScore >= 75 ? 'Strong' : validatedScore >= 50 ? 'Average' : 'Weak';
  scoreBadge.className = `score-badge ${validatedScore >= 75 ? 'badge-strong' : validatedScore >= 50 ? 'badge-average' : 'badge-weak'}`;
}

function setMessage(text) {
  projectSummary.textContent = text;
}

function renderChips(container, items, colorClass) {
  container.innerHTML = '';
  if (!items || !items.length) {
    const empty = document.createElement('div');
    empty.className = 'skill-chip empty-chip';
    empty.textContent = 'No items available';
    container.appendChild(empty);
    return;
  }
  items.forEach((item) => {
    const chip = document.createElement('div');
    chip.className = `skill-chip ${colorClass}`;
    chip.textContent = item;
    container.appendChild(chip);
  });
}

function isValidGithubUrl(value) {
  try {
    const url = new URL(value);
    return url.hostname.includes('github.com');
  } catch {
    return false;
  }
}

// FIX: parse owner/repo from URL — backend schema requires {owner, repo} not {repoUrl}
function parseGithubUrl(repoUrl) {
  try {
    const url = new URL(repoUrl);
    const parts = url.pathname.replace(/^\//, '').split('/');
    if (parts.length >= 2) {
      return { owner: parts[0], repo: parts[1] };
    }
  } catch {
    // fall through
  }
  return null;
}

async function validateRepo() {
  const repoUrl = repoInput.value.trim();
  if (!repoUrl || !isValidGithubUrl(repoUrl)) {
    alert('Enter a valid GitHub repository URL (e.g. https://github.com/owner/repo).');
    repoInput.focus();
    return;
  }

  const parsed = parseGithubUrl(repoUrl);
  if (!parsed) {
    alert('Could not parse owner and repo from the URL. Please use https://github.com/owner/repo format.');
    return;
  }

  validateButton.disabled = true;
  validateButton.textContent = 'Validating...';
  setMessage('Validating repository and fetching project metadata...');

  try {
    const response = await fetch(VALIDATE_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ owner: parsed.owner, repo: parsed.repo }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Validation request failed.');
    }

    // FIX: response field is `skills` not `skillsDetected`
    const result = await response.json();
    updateScore(result.score || 0);
    setMessage(result.summary || 'No summary available for this repository.');
    renderChips(projectSkills, result.skills, 'skill-chip-matched');
    renderChips(projectWeaknesses, result.weaknesses, 'skill-chip-missing');
  } catch (error) {
    setMessage(error.message || 'Unable to validate repository at this time.');
    updateScore(0);
    renderChips(projectSkills, [], 'skill-chip-matched');
    renderChips(projectWeaknesses, [], 'skill-chip-missing');
  } finally {
    validateButton.disabled = false;
    validateButton.textContent = 'Validate repo';
  }
}

function resetValidation() {
  repoInput.value = '';
  updateScore(0);
  scoreBadge.textContent = 'Pending';
  scoreBadge.className = 'score-badge';
  setMessage('Submit a repository to view the summary and commit highlights.');
  renderChips(projectSkills, [], 'skill-chip-matched');
  renderChips(projectWeaknesses, [], 'skill-chip-missing');
}

if (validateButton) validateButton.addEventListener('click', validateRepo);
if (clearValidation) clearValidation.addEventListener('click', resetValidation);

resetValidation();