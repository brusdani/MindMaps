document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    const overlay = document.getElementById('overlay');
    const spinner = document.getElementById('spinner');

    // Show spinner and overlay when the form is submitted
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            // Display overlay and spinner during form submission
            overlay.style.display = 'block';
            spinner.style.display = 'block';
        });
    });
});
