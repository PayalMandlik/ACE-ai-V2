const createRoadmapButton = document.getElementById('create-roadmap');
const resetRoadmapButton = document.getElementById('reset-roadmap');
const skillInput = document.getElementById('roadmap-skill');
const durationInput = document.getElementById('roadmap-duration');
const timelineTitle = document.getElementById('timeline-title');
const timelineRange = document.getElementById('timeline-range');
const timelineList = document.getElementById('timeline-list');

const ROADMAP_API = '/roadmap';

function buildTaskCard(day, task, details) {
  const item = document.createElement('div');
  item.className = 'timeline-item';
  item.innerHTML = `
    <button type="button" class="timeline-trigger">
      <span>Day ${day}</span>
      <span>${task}</span>
      <strong class="toggle-icon">+</strong>
    </button>
    <div class="timeline-details">
      <p>${details}</p>
    </div>
  `;

  const trigger = item.querySelector('.timeline-trigger');
  const detailPanel = item.querySelector('.timeline-details');
  const toggleIcon = item.querySelector('.toggle-icon');

  trigger.addEventListener('click', () => {
    const expanded = item.classList.toggle('expanded');
    detailPanel.style.maxHeight = expanded ? `${detailPanel.scrollHeight}px` : '0px';
    toggleIcon.textContent = expanded ? '−' : '+';
  });

  return item;
}

function renderTimeline(duration, blocks) {
  timelineList.innerHTML = '';
  if (!blocks || !blocks.length) {
    timelineList.innerHTML = `
      <div class="timeline-item empty-state">
        <p class="text-muted">No roadmap tasks available.</p>
      </div>
    `;
    return;
  }

  blocks.forEach((block, index) => {
    if (typeof block === 'string') {
      // plain string fallback
      timelineList.appendChild(buildTaskCard(index + 1, `Day ${index + 1}`, block));
    } else {
      // FIX: backend roadmap_agent returns {day, task} objects — use task as both label and detail
      const day = block.day || index + 1;
      const label = block.title || block.task || `Day ${day}`;
      const detail = block.details || block.description || block.task || '';
      timelineList.appendChild(buildTaskCard(day, label, detail));
    }
  });
}

async function fetchRoadmap() {
  const skill = skillInput.value.trim();
  const duration = Number(durationInput.value);

  if (!skill) {
    alert('Please enter a target skill.');
    skillInput.focus();
    return;
  }

  if (!duration || duration < 7 || duration > 90) {
    alert('Please enter a valid duration between 7 and 90 days.');
    durationInput.focus();
    return;
  }

  createRoadmapButton.disabled = true;
  createRoadmapButton.textContent = 'Building...';

  try {
    const response = await fetch(ROADMAP_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skill, duration: String(duration) }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Roadmap generation failed.');
    }

    const result = await response.json();
    timelineTitle.textContent = result.summary || `Roadmap for ${skill}`;
    timelineRange.textContent = `${duration} days`;
    renderTimeline(duration, result.roadmap);
  } catch (error) {
    timelineTitle.textContent = 'Generation error';
    timelineRange.textContent = '0 days';
    timelineList.innerHTML = `
      <div class="timeline-item empty-state">
        <p class="text-muted">${error.message || 'Unable to build a roadmap right now.'}</p>
      </div>
    `;
  } finally {
    createRoadmapButton.disabled = false;
    createRoadmapButton.textContent = 'Create plan';
  }
}

function resetRoadmap() {
  skillInput.value = '';
  durationInput.value = '';
  timelineTitle.textContent = 'No roadmap created yet';
  timelineRange.textContent = '0 days';
  timelineList.innerHTML = `
    <div class="timeline-item empty-state">
      <p class="text-muted">Create a roadmap to see day-wise tasks and milestones.</p>
    </div>
  `;
}

if (createRoadmapButton) createRoadmapButton.addEventListener('click', fetchRoadmap);
if (resetRoadmapButton) resetRoadmapButton.addEventListener('click', resetRoadmap);

resetRoadmap();