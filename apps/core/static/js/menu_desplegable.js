// Este código se encarga de manejar la apertura y cierre del menú lateral en la aplicación.

document.addEventListener('DOMContentLoaded', function () {
    //Para buscar el botón que abre el menú lateral
    const menuBtn = document.getElementById('gcm-open-menu');
    //Para buscar el menú lateral que se muestra al hacer clic en el botón
    const sidebar = document.getElementById('gcm-sidebar-menu');
    //Para buscar la capa oscura que se muestra al abrir el menú
    const overlay = document.getElementById('gcm-overlay-layer');

    function toggleGcmMenu() {
        sidebar.classList.toggle('is-visible');
        overlay.classList.toggle('is-visible');
    }

    if (menuBtn) {
        menuBtn.addEventListener('click', toggleGcmMenu);
        overlay.addEventListener('click', toggleGcmMenu);
    }
});