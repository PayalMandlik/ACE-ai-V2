const LOGIN_PATH = '/auth/login';
const SIGNUP_PATH = '/auth/signup';
const DASHBOARD_PATH = 'pages/dashboard.html';

const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');

function setAlert(element, message, type = 'error') {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle('alert-error', type === 'error');
  element.classList.toggle('alert-success', type === 'success');
  element.classList.add('alert-visible');
}

function clearAlert(element) {
  if (!element) return;
  element.textContent = '';
  element.classList.remove('alert-error', 'alert-success', 'alert-visible');
}

function validateEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validatePassword(value) {
  return value.length >= 8;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || 'Request failed');
  }
  return data;
}

async function handleLogin(event) {
  event.preventDefault();
  const alertEl = document.getElementById('login-alert');
  clearAlert(alertEl);

  const email = loginForm.email.value.trim();
  const password = loginForm.password.value;

  if (!validateEmail(email)) {
    setAlert(alertEl, 'Please enter a valid email address.');
    return;
  }

  if (!validatePassword(password)) {
    setAlert(alertEl, 'Password must be at least 8 characters long.');
    return;
  }

  const submitButton = loginForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Signing in...';

  try {
    const result = await postJson(LOGIN_PATH, { email, password });
    localStorage.setItem('ace_token', result.token);
    localStorage.setItem('ace_user', JSON.stringify(result.user || { email }));
    window.location.href = DASHBOARD_PATH;
  } catch (error) {
    setAlert(alertEl, error.message || 'Unable to sign in. Please try again.');
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Log in';
  }
}

async function handleSignup(event) {
  event.preventDefault();
  const alertEl = document.getElementById('signup-alert');
  clearAlert(alertEl);

  const name = signupForm.name.value.trim();
  const email = signupForm.email.value.trim();
  const password = signupForm.password.value;
  const confirmPassword = signupForm.confirmPassword.value;

  if (name.length < 2) {
    setAlert(alertEl, 'Please enter your full name.');
    return;
  }

  if (!validateEmail(email)) {
    setAlert(alertEl, 'Please enter a valid email address.');
    return;
  }

  if (!validatePassword(password)) {
    setAlert(alertEl, 'Password must be at least 8 characters long.');
    return;
  }

  if (password !== confirmPassword) {
    setAlert(alertEl, 'Passwords do not match.');
    return;
  }

  const submitButton = signupForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Creating account...';

  try {
    await postJson(SIGNUP_PATH, {
      name,
      email,
      password,
    });
    setAlert(alertEl, 'Account created successfully. Redirecting to login...', 'success');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 1200);
  } catch (error) {
    setAlert(alertEl, error.message || 'Unable to create account. Please try again.');
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Create account';
  }
}

if (loginForm) {
  loginForm.addEventListener('submit', handleLogin);
}

if (signupForm) {
  signupForm.addEventListener('submit', handleSignup);
}
