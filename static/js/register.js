// REGISTER SCRIPT — valida y envía
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#registerForm');
    const submitBtn = document.querySelector('.btn-submit');
    const errorBox = document.querySelector('#registerError');

    if (!form || !submitBtn) return;

    submitBtn.addEventListener('click', function (e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const fullname = document.getElementById('fullname').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password1').value;
        const repeat = document.getElementById('password2').value;

        if (!username || !fullname || !email || !password || !repeat) {
            errorBox.textContent = "Todos los campos son obligatorios.";
            return;
        }

        if (password !== repeat) {
            errorBox.textContent = "Las contraseñas no coinciden.";
            return;
        }

        errorBox.textContent = ""; // limpiar errores
        form.submit();
    });
});

