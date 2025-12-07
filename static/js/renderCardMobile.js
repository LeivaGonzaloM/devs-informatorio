// Forzar fade-up visible en móviles
(function() {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        document.querySelectorAll('.fade-up').forEach(el => {
            el.classList.add('visible');
        });
    }
})();

// Cuando cierres el menú móvil
function closeMobileMenu() {
    mobileMenuBtn.classList.remove('active');
    mobileMenu.classList.remove('active');
    mobileMenuOverlay.classList.remove('active');
    document.body.style.overflow = ''; // ¡muy importante!
}
