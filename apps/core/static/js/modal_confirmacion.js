document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('customModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('confirmBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const triggers = document.querySelectorAll('.trigger-modal');

    // Al hacer click en cualquier botón que deba abrir el modal
    triggers.forEach(button => {
        button.addEventListener('click', () => {
            const url = button.getAttribute('data-url');
            const message = button.getAttribute('data-message');

            // Inyectar datos en el modal
            modalMessage.textContent = message;
            confirmBtn.href = url;

            // Copiar la clase de color del botón original al botón de confirmación
            const colorClass = button.classList.contains('btn-danger-custom')
                ? 'btn-danger-custom' : 'btn-primary-custom';
            confirmBtn.className = `btn-custom ${colorClass}`;

            // Abrir modal nativo
            modal.showModal();
        });
    });

    // Cerrar modal al hacer click en cancelar
    cancelBtn.addEventListener('click', () => {
        modal.close();
    });

    // Cerrar modal si se hace click fuera (en el backdrop)
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.close();
    });
});