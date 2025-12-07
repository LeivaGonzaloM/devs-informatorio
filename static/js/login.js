// LOGIN SCRIPT — simple, no interfiere con el template

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#loginForm');
    const submitBtn = document.querySelector('.btn-submit');

    if (form && submitBtn) {
        submitBtn.addEventListener('click', function () {
            form.submit();
        });
    }
});
