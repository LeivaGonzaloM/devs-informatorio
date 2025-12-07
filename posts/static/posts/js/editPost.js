console.log("FUNCIONAAAA!")
// editPost.js
document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('editPostForm');
    if (!editForm) return;

    const submitBtn = document.getElementById('editPostBtn');
    if (!submitBtn) return;

    editForm.addEventListener('submit', (e) => {
        e.preventDefault(); // previene envío inmediato

        // efecto visual
        submitBtn.textContent = 'TRANSMITTING...';
        submitBtn.style.background = 'linear-gradient(135deg, var(--primary-cyan), var(--primary-pink))';
        submitBtn.style.boxShadow = '0 0 30px rgba(0,255,255,0.6)';
        submitBtn.disabled = true;

        // enviar formulario tras 300ms
        setTimeout(() => {
            editForm.submit();
        }, 300);
    });
});



