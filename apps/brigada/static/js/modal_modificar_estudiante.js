// --- Funciones del Modal de Edición ---
function abrirModalEditar() {
    document.getElementById('modalEditarEstudiante').style.display = 'flex'; // o 'block' según tus estilos CSS
}

function cerrarModalEditar() {
    document.getElementById('modalEditarEstudiante').style.display = 'none';
    document.getElementById('errorAlertaEditar').innerText = ''; // Limpiar errores
}

// Manejar el envío del formulario
const formEditar = document.getElementById('formEditarEstudiante');
if (formEditar) {
    formEditar.addEventListener('submit', function(e) {
        e.preventDefault(); // Evitar recarga tradicional
        
        // Obtenemos el ID del estudiante del div oculto que ya tienes en el HTML
        const estudianteId = document.getElementById('metadata-estudiante').getAttribute('data-id');
        const formData = new FormData(this);

        // Hacemos la petición AJAX a tu endpoint de Django
        fetch(`/brigada/estudiante/editar/${estudianteId}/`, { // <- Ajusta esta URL a la tuya
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Para que Django detecte que es AJAX
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Si todo sale bien, recargamos la página para ver los cambios
                alert(data.message);
                window.location.reload();
            } else {
                // Si hay un error de validación, lo mostramos
                document.getElementById('errorAlertaEditar').innerText = data.error || 'Ocurrió un error al actualizar.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('errorAlertaEditar').innerText = 'Error de conexión con el servidor.';
        });
    });
}