document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    const overlay = document.getElementById('overlay');
    const spinner = document.getElementById('spinner');

    forms.forEach(form => {
        form.addEventListener('submit', function () {
            overlay.style.display = 'block';
            spinner.style.display = 'block';
        });
    });
});
