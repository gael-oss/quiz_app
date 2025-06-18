// static/js/ajax_quizzes.js

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('quiz-form');
  const spinner = document.getElementById('quiz-spinner');
  const tbody = document.querySelector('#quizzes-table tbody');

  // Création de quiz
  form.addEventListener('submit', e => {
    e.preventDefault();
    spinner.classList.remove('hidden');
    const data = new FormData(form);

    fetch(form.action, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: data
    })
    .then(res => res.json())
    .then(json => {
      spinner.classList.add('hidden');
      if (json.errors) {
        alert('Erreur : ' + JSON.stringify(json.errors));
      } else {
        // Construire la nouvelle ligne
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${json.titre}</td>
          <td>${json.classe}</td>
          <td>
            <button class="btn btn-small delete-quiz" data-pk="${json.pk}">🗑️</button>
          </td>`;
        tbody.prepend(tr);
        form.reset();
      }
    })
    .catch(err => {
      spinner.classList.add('hidden');
      console.error(err);
      alert('Erreur réseau');
    });
  });

  // Suppression de quiz
  tbody.addEventListener('click', e => {
    if (e.target.matches('.delete-quiz')) {
      const btn = e.target;
      const pk = btn.dataset.pk;
      spinner.classList.remove('hidden');
      fetch(`/teacher/quizzes/${pk}/delete/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      })
      .then(res => res.json())
      .then(json => {
        spinner.classList.add('hidden');
        if (json.deleted) {
          btn.closest('tr').remove();
        }
      })
      .catch(err => {
        spinner.classList.add('hidden');
        console.error(err);
      });
    }
  });
});
