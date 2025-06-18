// static/js/ajax_classes.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('class-form');
  const spinner = document.getElementById('class-spinner');
  const tableBody = document.querySelector('#classes-table tbody');

  form.addEventListener('submit', e => {
    e.preventDefault();
    spinner.classList.remove('hidden');
    const url = form.action;
    const data = new FormData(form);

    fetch(url, {
      method: 'POST',
      headers: {'X-Requested-With': 'XMLHttpRequest'},
      body: data
    })
    .then(resp => resp.json())
    .then(json => {
      spinner.classList.add('hidden');
      if (json.errors) {
        alert('Erreur : ' + JSON.stringify(json.errors));
      } else {
        // Ajout d’une nouvelle ligne au tableau
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${json.nom}</td>
          <td>
            <button class="btn btn-small delete-class" data-pk="${json.pk}">🗑️</button>
          </td>`;
        tableBody.prepend(tr);
        form.reset();
      }
    })
    .catch(err => {
      spinner.classList.add('hidden');
      alert('Erreur réseau');
      console.error(err);
    });
  });

  // Délégué pour les suppressions
  tableBody.addEventListener('click', e => {
    if (e.target.matches('.delete-class')) {
      const btn = e.target;
      const pk = btn.dataset.pk;
      spinner.classList.remove('hidden');
      fetch(`/teacher/classes/${pk}/delete/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      })
      .then(r => r.json())
      .then(j => {
        spinner.classList.add('hidden');
        if (j.deleted) {
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
