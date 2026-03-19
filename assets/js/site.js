
(function () {
  var themeKey = 'stock-theme';
  var root = document.documentElement;
  var current = localStorage.getItem(themeKey) || 'light';
  root.setAttribute('data-theme', current);

  var themeBtn = document.getElementById('theme-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem(themeKey, next);
    });
  }

  var dataEl = document.getElementById('report-data');
  var input = document.getElementById('site-search');
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-report-card]'));
  if (!input || !dataEl || cards.length === 0) return;

  var reports = [];
  try {
    reports = JSON.parse(dataEl.textContent || '[]');
  } catch (err) {
    reports = [];
  }

  function applyFilter(query) {
    var q = query.trim().toLowerCase();
    cards.forEach(function (card) {
      var hay = (card.getAttribute('data-search') || '').toLowerCase();
      card.style.display = !q || hay.indexOf(q) !== -1 ? '' : 'none';
    });
  }

  input.addEventListener('input', function () {
    applyFilter(input.value);
  });

  window.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
