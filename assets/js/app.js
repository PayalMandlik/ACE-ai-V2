function initializePageTransitions() {
  const body = document.body;
  body.classList.add('page-enter');

  const internalLinks = Array.from(document.querySelectorAll('a[href]')).filter((link) => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) {
      return false;
    }
    try {
      const url = new URL(href, window.location.href);
      return url.origin === window.location.origin && url.pathname !== window.location.pathname;
    } catch {
      return false;
    }
  });

  internalLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      body.classList.remove('page-enter');
      body.classList.add('page-exit');
      const target = link.href;
      window.setTimeout(() => {
        window.location.href = target;
      }, 240);
    });
  });
}

function typeText(element, text, speed = 30) {
  element.textContent = '';
  const chars = Array.from(text);
  let index = 0;
  element.classList.add('typing-active');

  const interval = window.setInterval(() => {
    if (index >= chars.length) {
      window.clearInterval(interval);
      element.classList.remove('typing-active');
      return;
    }
    element.textContent += chars[index];
    index += 1;
  }, speed);
}

function initializeTypingEffects() {
  const typedElements = document.querySelectorAll('[data-typing]');
  typedElements.forEach((element) => {
    const text = element.getAttribute('data-typing');
    if (text) {
      typeText(element, text, 30);
    }
  });
}

function initializeMobileNavigation() {
  const menuToggle = document.querySelector('.menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (!menuToggle || !sidebar) return;

  menuToggle.addEventListener('click', () => {
    const expanded = sidebar.classList.toggle('sidebar-expanded');
    menuToggle.classList.toggle('open', expanded);
    menuToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  });

  sidebar.querySelectorAll('.sidebar-nav a').forEach((link) => {
    link.addEventListener('click', () => {
      if (sidebar.classList.contains('sidebar-expanded')) {
        sidebar.classList.remove('sidebar-expanded');
        menuToggle.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initializePageTransitions();
  initializeTypingEffects();
  initializeMobileNavigation();
});
