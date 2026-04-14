const SUGGESTIONS_API = '/suggestions';

const focusAreas = document.getElementById('focus-areas');
const adviceList = document.getElementById('advice-list');
const avoidList = document.getElementById('avoid-list');
const refreshButton = document.getElementById('refresh-suggestions');

function renderStringItems(container, items, emptyText) {
  container.innerHTML = '';
  if (!items || !items.length) {
    const empty = document.createElement('div');
    empty.className = 'suggestion-card empty-card';
    empty.textContent = emptyText;
    container.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'suggestion-card';
    // FIX: backend returns List[str], not objects with title/description
    if (typeof item === 'string') {
      card.innerHTML = `<p>${item}</p>`;
    } else {
      card.innerHTML = `<h4>${item.title || ''}</h4><p>${item.description || item.text || ''}</p>`;
    }
    container.appendChild(card);
  });
}

async function loadSuggestions() {
  refreshButton.disabled = true;
  refreshButton.textContent = 'Loading...';

  try {
    const response = await fetch(SUGGESTIONS_API);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Unable to load suggestions.');
    }

    // FIX: response is {summary, suggestions: List[str], priority_actions: List[str]}
    // Map: suggestions split across focus/advice panels; priority_actions → avoid panel
    const data = await response.json();

    if (data.summary) {
      const summaryEl = document.querySelector('.suggestions-hero [data-typing]') ||
                        document.querySelector('.suggestions-hero p:last-child');
      if (summaryEl) summaryEl.textContent = data.summary;
    }

    const allSuggestions = data.suggestions || [];
    const half = Math.ceil(allSuggestions.length / 2);
    renderStringItems(focusAreas, allSuggestions.slice(0, half), 'No focus areas available.');
    renderStringItems(adviceList, allSuggestions.slice(half), 'No advice available.');
    renderStringItems(avoidList, data.priority_actions || [], 'No priority actions available.');
  } catch (error) {
    renderStringItems(focusAreas, [], error.message);
    renderStringItems(adviceList, [], error.message);
    renderStringItems(avoidList, [], error.message);
  } finally {
    refreshButton.disabled = false;
    refreshButton.textContent = 'Refresh';
  }
}

if (refreshButton) refreshButton.addEventListener('click', loadSuggestions);

loadSuggestions();