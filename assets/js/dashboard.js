const DASHBOARD_API = '/api/dashboard';

const profileName = document.getElementById('profile-name');
const profileXp = document.getElementById('profile-xp');
const profileLevel = document.getElementById('profile-level');
const profileStreak = document.getElementById('profile-streak');
const dashboardStatus = document.getElementById('dashboard-status');
const resumeScore = document.getElementById('resume-score');
const skillReadiness = document.getElementById('skill-readiness');
const validationStatus = document.getElementById('validation-status');
const nextMilestone = document.getElementById('next-milestone');
const activityFeed = document.getElementById('activity-feed');
const refreshButton = document.getElementById('refresh-dashboard');
const logoutButton = document.getElementById('logout-button');

function getToken() {
  return localStorage.getItem('ace_token');
}

function applyMetric(element, value) {
  if (element) element.textContent = value;
}

function renderActivity(items = []) {
  activityFeed.innerHTML = '';
  if (!items.length) {
    activityFeed.innerHTML = `
      <div class="activity-item">
        <div>
          <p class="activity-title">No recent events</p>
          <p class="text-muted">Your feed will update after actions and assessments.</p>
        </div>
        <span class="timestamp">--</span>
      </div>
    `;
    return;
  }

  items.slice(0, 5).forEach((item) => {
    const block = document.createElement('div');
    block.className = 'activity-item';
    block.innerHTML = `
      <div>
        <p class="activity-title">${item.title}</p>
        <p class="text-muted">${item.description}</p>
      </div>
      <span class="timestamp">${item.time}</span>
    `;
    activityFeed.appendChild(block);
  });
}

async function fetchDashboard() {
  const token = getToken();
  if (!token) {
    window.location.href = '../login.html';
    return;
  }

  refreshButton.disabled = true;
  refreshButton.textContent = 'Refreshing...';

  try {
    const response = await fetch(DASHBOARD_API, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Unable to load dashboard data.');
    }

    const data = await response.json();
    const profile = data.profile || {};
    const stats = data.stats || {};

    applyMetric(profileName, profile.name || 'Career strategist');
    applyMetric(profileXp, profile.xp ? `${profile.xp} XP` : '0 XP');
    applyMetric(profileLevel, profile.level ? `Level ${profile.level}` : 'Level 1');
    applyMetric(profileStreak, profile.streak ? `${profile.streak} days` : '0 days');
    applyMetric(resumeScore, stats.resumeScore ? `${stats.resumeScore}%` : '--');
    applyMetric(skillReadiness, stats.skillReadiness ? `${stats.skillReadiness}%` : '--');
    applyMetric(validationStatus, stats.validationStatus || '--');
    applyMetric(nextMilestone, stats.nextMilestone || 'Set your next goal');
    dashboardStatus.textContent = data.status || 'Live';
    renderActivity(data.activity);
  } catch (error) {
    dashboardStatus.textContent = 'Offline';
    activityFeed.innerHTML = `
      <div class="activity-item">
        <div>
          <p class="activity-title">Unable to load data</p>
          <p class="text-muted">Check your connection or sign in again.</p>
        </div>
        <span class="timestamp">!</span>
      </div>
    `;
  } finally {
    refreshButton.disabled = false;
    refreshButton.textContent = 'Refresh';
  }
}

function handleLogout() {
  localStorage.removeItem('ace_token');
  localStorage.removeItem('ace_user');
  window.location.href = '../login.html';
}

if (refreshButton) {
  refreshButton.addEventListener('click', fetchDashboard);
}

if (logoutButton) {
  logoutButton.addEventListener('click', handleLogout);
}

fetchDashboard();
