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
                mostrarError('Por favor, selecciona una carrera válida.');
                return;
            }

            // Construcción de la URL (Asegúrate que coincida con tu urls.py)
            const url = `/brigada/${brigadaId}/${carreraId}/estudiante/agregar/`;

            try {
                const btnSubmit = form.querySelector('button[type="submit"]');
                if(btnSubmit) btnSubmit.disabled = true;

                const response = await fetch(url, { 
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        // Extraemos el CSRF token del formulario
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value 
                    }
                });

                const data = await response.json();

                if (data.exito) {
                    // ÉXITO: Recargamos para ver los cambios y mensajes de Django
                    modal.style.display = 'none';
                    window.location.reload(); 
                } else {
                    // ERROR DEL SERVIDOR (Validación, etc.)
                    mostrarError(data.mensaje || 'Error al guardar el estudiante.');
                    if(btnSubmit) btnSubmit.disabled = false;
                }

            } catch (error) {
                console.error("Error en Fetch:", error);
                mostrarError('Error de conexión con el servidor.');
                const btnSubmit = form.querySelector('button[type="submit"]');
                if(btnSubmit) btnSubmit.disabled = false;
            }
        });
    }

    // Función auxiliar para mostrar errores de forma limpia
    function mostrarError(mensaje) {
        if (divError) {
            divError.textContent = mensaje;
            divError.style.display = 'block';
            divError.style.color = '#e74c3c';
            divError.style.marginTop = '10px';
        } else {
            alert(mensaje);
        }
    }
});