// --- Funciones del Modal de Edición del Proyecto ---

function abrirModalEditarProyecto() {
    document.getElementById('modalEditarProyecto').style.display = 'flex';
}

function cerrarModalEditarProyecto() {
    document.getElementById('modalEditarProyecto').style.display = 'none';
    const alerta = document.getElementById('errorAlertaEditarProyecto');
    if (alerta) alerta.innerText = ''; 
}

const formEditarProyecto = document.getElementById('formEditarProyecto');

if (formEditarProyecto) {
    // CORRECCIÓN: Agregamos "async" antes de la función
    formEditarProyecto.addEventListener('submit', async function(e) {
        e.preventDefault(); 
        
        const metadata = document.getElementById('metadata-proyecto');
        const proyectoId = metadata ? metadata.getAttribute('data-id') : null;
        const alertaUI = document.getElementById('errorAlertaEditarProyecto');
        const btnSubmit = this.querySelector('button[type="submit"]');
        
        // 1. Obtener el token CSRF
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfInput ? csrfInput.value : '';

        if (!proyectoId) {
            console.error("No se encontró el ID del proyecto");
            return;
        }

        const formData = new FormData(this); // (Línea duplicada eliminada)

        try {
            if (btnSubmit) btnSubmit.disabled = true;
            if (alertaUI) alertaUI.style.display = 'none';

            // 2. Petición al servidor
            const response = await fetch(`/brigada/proyecto/editar_proyecto/${proyectoId}/`, { 
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // ÉXITO
                window.location.reload();
            } else {
                // ERROR DE VALIDACIÓN o ERROR FATAL
                if (data.fatal_error) {
                    window.location.reload();
                    return;
                }

                if (alertaUI) {
                    alertaUI.style.display = 'block';
                    alertaUI.style.color = '#ff4b2b';
                    alertaUI.innerText = data.message || 'Error desconocido';
                }
                
                if (btnSubmit) btnSubmit.disabled = false;
            }

        } catch (error) {
            console.error('Error en la comunicación:', error);
            if (alertaUI) {
                alertaUI.style.display = 'block';
                alertaUI.innerText = 'Error de conexión con el servidor.';
            }
            if (btnSubmit) btnSubmit.disabled = false;
        }
    });
}