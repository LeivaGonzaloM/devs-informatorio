// patchCreatePost.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('createForm');
    const submitBtn = document.querySelector('.btn-submit');

    if (!form || !submitBtn) return;

    // Clonamos el botón para eliminar cualquier event listener existente
    const newBtn = submitBtn.cloneNode(true);
    submitBtn.parentNode.replaceChild(newBtn, submitBtn);

    // Solo dejamos animaciones de hover (opcional)
    newBtn.addEventListener('mouseenter', () => {
        newBtn.style.boxShadow = '0 0 30px rgba(0, 255, 255, 0.6)';
    });
    newBtn.addEventListener('mouseleave', () => {
        newBtn.style.boxShadow = '';
    });

    // Esto asegura que el submit funcione normalmente y Django haga el redirect
    form.addEventListener('submit', () => {
        // Aquí podrías agregar alguna animación ligera si querés, pero sin e.preventDefault()
        newBtn.textContent = 'Creando...';
    });
});
