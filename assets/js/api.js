const API_BASE_URL = '';

function getAuthToken() {
  return localStorage.getItem('ace_token');
}

function setAuthToken(token) {
  if (token) {
    localStorage.setItem('ace_token', token);
  }
}

function removeAuthToken() {
  localStorage.removeItem('ace_token');
}

function buildHeaders({ useAuth = true, contentType = 'application/json' } = {}) {
  const headers = {};

  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  if (useAuth) {
    const token = getAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  return headers;
}

async function parseResponse(response) {
  const text = await response.text();
  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }

  if (!response.ok) {
    const error = new Error(data?.message || response.statusText || 'API request failed');
    error.status = response.status;
    error.payload = data;
    throw error;
  }

  return data;
}

async function apiRequest(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const { method = 'GET', body = null, useAuth = true, isJson = true } = options;

  const headers = buildHeaders({ useAuth, contentType: isJson ? 'application/json' : null });

  const init = {
    method,
    headers,
  };

  if (body !== null) {
    init.body = isJson ? JSON.stringify(body) : body;
  }

  const response = await fetch(url, init);
  return parseResponse(response);
}

function login(email, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: { email, password },
    useAuth: false,
  }).then((data) => {
    if (data?.token) {
      setAuthToken(data.token);
    }
    return data;
  });
}

function signup(name, email, password) {
  return apiRequest('/auth/signup', {
    method: 'POST',
    body: { name, email, password },
    useAuth: false,
  });
}

function analyzeResume(formData) {
  return apiRequest('/resume/analyze', {
    method: 'POST',
    body: formData,
    isJson: false,
  });
}

function analyzeGap(role, preferredSkills = []) {
  return apiRequest('/gap/analyze', {
    method: 'POST',
    body: { role, preferredSkills },
  });
}

function validateGithub(ownerOrUrl, repo) {
  let payload;
  if (typeof ownerOrUrl === 'string' && repo) {
    payload = { owner: ownerOrUrl, repo };
  } else if (typeof ownerOrUrl === 'string') {
    payload = { repoUrl: ownerOrUrl };
  } else {
    payload = ownerOrUrl;
  }

  return apiRequest('/validate/github', {
    method: 'POST',
    body: payload,
  });
}

function createRoadmap(skill, duration) {
  return apiRequest('/roadmap', {
    method: 'POST',
    body: { skill, duration },
  });
}

function fetchAssessmentQuestions() {
  return apiRequest('/assessment', {
    method: 'GET',
  });
}

function submitAssessment(answers) {
  return apiRequest('/assessment/submit', {
    method: 'POST',
    body: { answers },
  });
}

function fetchSuggestions() {
  return apiRequest('/suggestions', {
    method: 'GET',
  });
}

function fetchDashboard() {
  return apiRequest('/api/dashboard', {
    method: 'GET',
  });
}

function logout() {
  removeAuthToken();
}

window.ACE_API = {
  login,
  signup,
  analyzeResume,
  analyzeGap,
  validateGithub,
  createRoadmap,
  fetchAssessmentQuestions,
  submitAssessment,
  fetchSuggestions,
  fetchDashboard,
  logout,
};
