// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('spinner-overlay');

  // Affiche le spinner
  function showSpinner() {
    overlay.classList.add('active');
  }
  // Cache le spinner
  function hideSpinner() {
    overlay.classList.remove('active');
  }

  // Interception de fetch pour show/hide
  const _fetch = window.fetch;
  window.fetch = function(...args) {
    showSpinner();
    return _fetch(...args)
      .then(res => {
        hideSpinner();
        if (!res.ok) {
          res.text().then(text => {
            Toastify({
              text: `Erreur réseau : ${res.status}`,
              duration: 4000,
              gravity: 'top',
              position: 'right',
              backgroundColor: 'var(--danger)'
            }).showToast();
          });
        }
        return res;
      })
      .catch(err => {
        hideSpinner();
        Toastify({
          text: `Erreur réseau : ${err.message}`,
          duration: 4000,
          gravity: 'top',
          position: 'right',
          backgroundColor: 'var(--danger)'
        }).showToast();
        throw err;
      });
  };
});
