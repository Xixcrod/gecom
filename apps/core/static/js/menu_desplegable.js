document.addEventListener('DOMContentLoaded', function () {
    const menuBtn = document.getElementById('gcm-open-menu');
    const sidebar = document.getElementById('gcm-sidebar-menu');
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