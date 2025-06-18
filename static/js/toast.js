/**
 * Affiche les messages Django via Toastify.
 * Nécessite le rendu JSON des messages dans la balise <script id="messages-data">.
 */
document.addEventListener('DOMContentLoaded', () => {
  const data = JSON.parse(document.getElementById('messages-data').textContent);
  data.forEach(msg => {
    Toastify({
      text: msg.message,
      duration: 3000,
      close: true,
      gravity: "top",
      position: "right",
      backgroundColor: msg.tags.includes("success") ? "var(--accent)" : "var(--primary)"
    }).showToast();
  });
});
