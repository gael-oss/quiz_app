/**
 * Démarre un compte à rebours.
 *
 * @param {number} duration - Durée en secondes.
 * @param {HTMLElement} display - Élément où afficher le temps.
 * @param {HTMLFormElement} form - Formulaire à soumettre à la fin.
 */
function startTimer(duration, display, form) {
  let timer = duration, minutes, seconds;
  const interval = setInterval(() => {
    minutes = Math.floor(timer / 60);
    seconds = timer % 60;
    display.textContent = 
      String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    if (--timer < 0) {
      clearInterval(interval);
      // Soumission automatique du formulaire
      form.submit();
    }
  }, 1000);
}
