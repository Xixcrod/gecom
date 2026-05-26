document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('customModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('confirmBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const closeBtn = document.getElementById('closeModalBtn'); // Añadimos el botón (X)
    const triggers = document.querySelectorAll('.trigger-modal');

    // Función unificada para cerrar la modal
    const cerrarModal = () => {
        // En lugar de modal.close(), ocultamos el div
        modal.style.display = 'none';
    };

    // Al hacer click en cualquier botón que deba abrir el modal
    triggers.forEach(button => {
        button.addEventListener('click', () => {
            const url = button.getAttribute('data-url');
            const message = button.getAttribute('data-message');

            // Inyectar datos en el modal
            modalMessage.textContent = message;
            confirmBtn.href = url;

            // Copiar el color del botón original al botón de confirmación
            // Verificamos si el botón presionado usa alguna de las nuevas clases rojas
            if (button.classList.contains('btn-danger') || button.classList.contains('btn-respaldo-peligro')) {
                // Usamos la clase global roja (Si usaste el diseño autónomo, cambia esto a 'btn-respaldo-peligro')
                confirmBtn.className = 'btn-danger'; 
            } else {
                // Usamos la clase global azul (Si usaste el diseño autónomo, cambia esto a 'btn-respaldo-primario')
                confirmBtn.className = 'btn-save'; 
            }

            // Abrir modal nativo usando Flexbox en lugar de showModal()
            modal.style.display = 'flex';
        });
    });

    // Cerrar modal al hacer click en cancelar o en la (X)
    if (cancelBtn) cancelBtn.addEventListener('click', cerrarModal);
    if (closeBtn) closeBtn.addEventListener('click', cerrarModal);

    // Cerrar modal si se hace click fuera (en el fondo oscuro)
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            cerrarModal();
        }
    });
});