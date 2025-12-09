console.log("editInforme.js cargado correctamente");

// editInforme.js
document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('editInformeForm');
    if (!editForm) return;

    const submitBtn = document.getElementById('editInformeBtn');
    if (!submitBtn) return;

    editForm.addEventListener('submit', (e) => {
        e.preventDefault(); // evita envío instantáneo

        // Animación futurista
        submitBtn.textContent = 'TRANSMITTING...';
        submitBtn.style.background = 'linear-gradient(135deg, var(--primary-cyan), var(--primary-pink))';
        submitBtn.style.boxShadow = '0 0 30px rgba(0,255,255,0.6)';
        submitBtn.disabled = true;

        // Enviar el form realmente
        setTimeout(() => {
            editForm.submit();
        }, 300);
    });
});
