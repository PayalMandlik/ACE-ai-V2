const analyzeGapButton = document.getElementById('analyze-gap');
const clearRoleButton = document.getElementById('clear-role');
const targetRoleInput = document.getElementById('target-role');
const skillTagsContainer = document.getElementById('skill-tags');
const matchedCount = document.getElementById('matched-count');
const missingCount = document.getElementById('missing-count');
const priorityCount = document.getElementById('priority-count');
const matchedSkills = document.getElementById('matched-skills');
const missingSkills = document.getElementById('missing-skills');
const prioritySkills = document.getElementById('priority-skills');

const GAP_API = '/gap/analyze';

let skillTags = [];

function createTag(text) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'tag-chip';
  button.textContent = text;
  button.addEventListener('click', () => removeTag(text));
  return button;
}

function renderTags() {
  skillTagsContainer.innerHTML = '';
  if (skillTags.length) {
    skillTags.forEach((skill) => skillTagsContainer.appendChild(createTag(skill)));
  } else {
    const hint = document.createElement('span');
    hint.className = 'text-muted';
    hint.textContent = 'Add skills that matter for the role.';
    skillTagsContainer.appendChild(hint);
  }

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'tag-input-field';
  input.placeholder = 'Type a skill and press Enter';
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      addTag(input.value);
      input.value = '';
    }
  });

  skillTagsContainer.appendChild(input);
}

function addTag(text) {
  const cleaned = text.trim();
  if (!cleaned || skillTags.includes(cleaned)) return;
  skillTags.push(cleaned);
  renderTags();
}

function removeTag(text) {
  skillTags = skillTags.filter((tag) => tag !== text);
  renderTags();
}

function displaySkills(container, skills, type) {
  container.innerHTML = '';
  if (!skills || !skills.length) {
    container.innerHTML = `<div class="skill-chip empty-chip">No ${type} skills found</div>`;
    return;
  }
  skills.forEach((skill) => {
    const chip = document.createElement('div');
    chip.className = `skill-chip skill-chip-${type}`;
    chip.textContent = skill;
    container.appendChild(chip);
  });
}

async function fetchGapAnalysis() {
  const role = targetRoleInput.value.trim();
  if (!role) {
    alert('Please enter a target role to analyze.');
    targetRoleInput.focus();
    return;
  }

  analyzeGapButton.disabled = true;
  analyzeGapButton.textContent = 'Analyzing...';

  try {
    // FIX: schema expects target_role and resume_skills
    const response = await fetch(GAP_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_role: role,
        resume_skills: skillTags,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Skill gap analysis failed.');
    }

    // FIX: response fields are matched, missing, priority (not camelCase)
    const result = await response.json();
    matchedCount.textContent = result.matched?.length || 0;
    missingCount.textContent = result.missing?.length || 0;
    priorityCount.textContent = result.priority?.length || 0;
    displaySkills(matchedSkills, result.matched, 'matched');
    displaySkills(missingSkills, result.missing, 'missing');
    displaySkills(prioritySkills, result.priority, 'priority');
  } catch (error) {
    alert(error.message || 'Unable to complete skill gap analysis.');
  } finally {
    analyzeGapButton.disabled = false;
    analyzeGapButton.textContent = 'Analyze role';
  }
}

function clearForm() {
  targetRoleInput.value = '';
  skillTags = [];
  renderTags();
  matchedCount.textContent = '0';
  missingCount.textContent = '0';
  priorityCount.textContent = '0';
  displaySkills(matchedSkills, [], 'matched');
  displaySkills(missingSkills, [], 'missing');
  displaySkills(prioritySkills, [], 'priority');
}

if (skillTagsContainer) renderTags();
if (analyzeGapButton) analyzeGapButton.addEventListener('click', fetchGapAnalysis);
if (clearRoleButton) clearRoleButton.addEventListener('click', clearForm);

clearForm();