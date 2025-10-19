let ajaxSent = false;

window.addEventListener('scroll', function () {
  if (ajaxSent) return; // Если запрос уже был отправлен — выходим

  const targetDiv = document.getElementById('target-div');
  const rect = targetDiv.getBoundingClientRect();
  const isVisible = rect.top <= window.innerHeight;

  if (isVisible) {
    ajaxSent = true;

    // Отправляем AJAX-запрос
    
  }
});