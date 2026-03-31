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
    formEditarProyecto.addEventListener('submit', function(e) {
        e.preventDefault(); 
        
        const proyectoId = document.getElementById('metadata-proyecto').getAttribute('data-id');
        const formData = new FormData(this);
        const alertaUI = document.getElementById('errorAlertaEditarProyecto');

        // URL conectada a la vista que acabamos de crear en Python
        fetch(`/brigada/proyecto/editar_proyecto/${proyectoId}/`, { 
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Éxito: Mostrar verde, bloquear botón, alertar y recargar
                alertaUI.style.display = 'block'; // Asegurar visibilidad
                alertaUI.style.color = 'green';
                alertaUI.innerText = data.message;

                const btn = formEditarProyecto.querySelector('button[type="submit"]');
                if (btn) btn.disabled = true;

                alert("✅ " + data.message);
                
                cerrarModalEditarProyecto();
                window.location.reload();
                
            } else {
                // Error desde Python: Mostrar en rojo
                alertaUI.style.display = 'block';
                alertaUI.style.color = 'red';
                alertaUI.innerText = data.error || 'Ocurrió un error al actualizar.';
                console.error("Error validación:", data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alertaUI.style.display = 'block';
            alertaUI.style.color = 'red';
            alertaUI.innerText = 'Error de conexión con el servidor.';
        });
    });
}