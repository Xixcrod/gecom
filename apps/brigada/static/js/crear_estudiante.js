document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('estudiante-modal');
    const btnAbrir = document.getElementById('estudiante-btn-nuevo');
    const btnCerrar = document.getElementById('estudiante-btn-cerrar');
    const form = document.getElementById('estudiante-form');
    const divError = document.getElementById('estudiante-error');

    // --- 1. Manejo del Modal ---
    if (btnAbrir) {
        btnAbrir.addEventListener('click', () => {
            modal.style.display = 'flex'; // Aseguramos que sea flex para centrar el contenido
            if (divError) divError.style.display = 'none'; 
            form.reset(); 
        });
    }

    if (btnCerrar) {
        btnCerrar.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Cerrar al hacer clic en el fondo oscuro
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // --- 2. Envío del formulario vía Fetch ---
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); 

            const formData = new FormData(form);
            if (divError) divError.style.display = 'none';

            // Obtenemos los IDs necesarios para la URL
            const brigadaId = formData.get('brigada_id');
            const carreraId = formData.get('carrera_id');

            // Validación rápida en cliente
            if (!brigadaId || !carreraId) {
                alert('Por favor, selecciona una carrera válida.');
                return;
            }

            // Construcción de la URL (Asegúrate que coincida con tu urls.py)
            const url = `/brigada/${brigadaId}/${carreraId}/estudiante/agregar/`;

            try {
                const btnSubmit = form.querySelector('button[type="submit"]');
                // Deshabilitar botón para evitar doble envío
                if(btnSubmit) btnSubmit.disabled = true;

                await fetch(url, { 
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value 
                    }
                });

                window.location.reload();


            } catch (error) {
                // Este catch solo se activa si hay un fallo de red o el servidor cae.
                console.error("Error en Fetch:", error);
                alert('Error de conexión con el servidor. Revisa tu internet.');
                
                // Si falla la red, habilitamos el botón de nuevo
                const btnSubmit = form.querySelector('button[type="submit"]');
                if (btnSubmit) btnSubmit.disabled = false;
            }
        });
    }
});