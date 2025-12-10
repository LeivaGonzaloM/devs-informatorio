console.log('darkmode.js cargado'); 
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.querySelector('.dark-mode');
    const html = document.documentElement; // <html>

    // Cargar estado guardado
    if (localStorage.getItem('darkMode') === 'true') {
        html.setAttribute('data-bs-theme', 'dark');
        darkModeToggle.classList.add('active'); // activa animación
    } else {
        html.setAttribute('data-bs-theme', 'light');
        darkModeToggle.classList.remove('active');
    }

    // Toggle al hacer click
    darkModeToggle.addEventListener('click', () => {
        darkModeToggle.classList.toggle('active'); // animación
        const isActive = darkModeToggle.classList.contains('active');

        // Cambia data-bs-theme según el estado
        html.setAttribute('data-bs-theme', isActive ? 'dark' : 'light');

        // Guarda en localStorage
        localStorage.setItem('darkMode', isActive ? 'true' : 'false');
    });
});

