// Welcome page script for Phishing URL Detector extension

document.addEventListener('DOMContentLoaded', function() {
  const closeButton = document.getElementById('closeButton');
  if (closeButton) {
    closeButton.addEventListener('click', function() {
      window.close();
    });
  }

  // Check if detector is running
  fetch('http://localhost:8501')
    .then(response => {
      if (response.ok) {
        const warningSection = document.querySelector('.warning');
        if (warningSection) {
          warningSection.style.display = 'none';
        }
      }
    })
    .catch(() => {
      // Detector not running, warning already shown
    });
});
