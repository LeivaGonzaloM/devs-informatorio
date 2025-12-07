
document.addEventListener("DOMContentLoaded", function() {
    // Seleccionamos todas las tarjetas con la clase específica
    const cards = document.querySelectorAll('.cardPost');

    cards.forEach(card => {
        // Obtenemos la URL desde un atributo data
        const url = card.dataset.href;
        if (url) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                window.location.href = url;
            });
        }
    });
});

