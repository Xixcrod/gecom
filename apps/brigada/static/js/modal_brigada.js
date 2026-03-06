function toggleModal(show) {
    const modal = document.getElementById('modalBrigada');
    if (!modal) return;
    
    modal.style.display = show ? 'flex' : 'none';
    
    if (show) {
        const input = modal.querySelector('input[name="nombre"]');
        if (input) input.focus();
    }
}

function handleOutsideClick(event) {
    const modal = document.getElementById('modalBrigada');
    if (event.target === modal) {
        toggleModal(false);
    }
}

// Lógica para ocultar alertas (si las usas)
window.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert-msg');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});