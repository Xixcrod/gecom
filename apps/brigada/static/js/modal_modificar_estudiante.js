// --- Funciones del Modal de Edición ---
function abrirModalEditar() {
    document.getElementById('modalEditarEstudiante').style.display = 'flex';
}

function cerrarModalEditar() {
    document.getElementById('modalEditarEstudiante').style.display = 'none';
    const alerta = document.getElementById('errorAlertaEditar');
    if (alerta) {
        alerta.style.display = 'none';
        alerta.innerText = '';
    }
}

const formEditar = document.getElementById('formEditarEstudiante');

if (formEditar) {
    // Usamos async para mantener el estándar moderno
    formEditar.addEventListener('submit', async function(e) {
        e.preventDefault(); 
        
        const metadata = document.getElementById('metadata-estudiante');
        const estudianteId = metadata ? metadata.getAttribute('data-id') : null;
        const alertaUI = document.getElementById('errorAlertaEditar');
        const btnSubmit = this.querySelector('button[type="submit"]');
        
        // Obtener el token CSRF (Asumiendo que tienes {% csrf_token %} en tu form HTML)
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfInput ? csrfInput.value : '';

        if (!estudianteId) {
            console.error("No se encontró el ID del estudiante");
            return;
        }

        const formData = new FormData(this);

        try {
            if (btnSubmit) btnSubmit.disabled = true;
            if (alertaUI) alertaUI.style.display = 'none';

            // Petición al servidor
            const response = await fetch(`/brigada/estudiante/editar/${estudianteId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken // Obligatorio para Django
                }
            });

            // Convertimos la respuesta
            const data = await response.json();

            if (response.ok && data.success) {
                // ÉXITO: Recargamos la página (ya quitamos el alert manual)
                // Django mostrará la notificación verde de messages.success
                window.location.reload();
            } else {
                // ERROR CRÍTICO
                if (data.fatal_error) {
                    window.location.reload();
                    return;
                }

                // ERRORES DE VALIDACIÓN: Se muestran directo en el modal
                if (alertaUI) {
                    alertaUI.style.display = 'block';
                    alertaUI.style.color = '#ff4b2b';
                    alertaUI.innerText = data.message || 'Error desconocido';
                }
                
                if (btnSubmit) btnSubmit.disabled = false;
            }

        } catch (error) {
            console.error('Error de conexión:', error);
            if (alertaUI) {
                alertaUI.style.display = 'block';
                alertaUI.innerText = 'Error de conexión con el servidor.';
            }
            if (btnSubmit) btnSubmit.disabled = false;
        }
    });
}