// Darkmode definitivo
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".dark-mode");
  const html = document.documentElement;

  if (!toggle) {
    console.warn("No se encontró el toggle de darkmode");
    return;
  }

  // Función para aplicar tema
  function applyTheme(isDark) {
    html.setAttribute("data-bs-theme", isDark ? "dark" : "light");
    toggle.classList.toggle("active", isDark);
    localStorage.setItem("darkMode", isDark ? "true" : "false");
  }

  // Cargar estado guardado
  applyTheme(localStorage.getItem("darkMode") === "true");

  // Click toggle
  toggle.addEventListener("click", () => {
    const isActive = toggle.classList.contains("active");
    applyTheme(!isActive);
  });

  // Evitar que otros scripts sobrescriban el tema
  const observer = new MutationObserver(() => {
    const isDark = localStorage.getItem("darkMode") === "true";
    if (html.getAttribute("data-bs-theme") !== (isDark ? "dark" : "light")) {
      html.setAttribute("data-bs-theme", isDark ? "dark" : "light");
    }
  });
  observer.observe(html, { attributes: true, attributeFilter: ["data-bs-theme"] });
});
