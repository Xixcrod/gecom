document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('estudiante-modal');
    const btnAbrir = document.getElementById('estudiante-btn-nuevo');
    const btnCerrar = document.getElementById('estudiante-btn-cerrar');
    const form = document.getElementById('estudiante-form');
    const errorDivEstudiante = document.getElementById('error-estudiante-ajax');

    // Función para mostrar errores
    function mostrarErrorEstudiante(mensaje) {
        if (!errorDivEstudiante) return;
        errorDivEstudiante.style.display = 'block';
        errorDivEstudiante.innerHTML = `<div class="error-modal-msg"><i class="fas fa-exclamation-circle"></i> ${mensaje}</div>`;
    }

    // --- 1. Manejo del Modal ---
    if (btnAbrir) {
        btnAbrir.addEventListener('click', () => {
            modal.style.display = 'flex'; 
            if (errorDivEstudiante) {
                errorDivEstudiante.style.display = 'none';
                errorDivEstudiante.innerHTML = '';
            }
            form.reset(); 
        });
    }

    if (btnCerrar) {
        btnCerrar.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

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
            
            // Ocultar errores al reintentar
            if (errorDivEstudiante) {
                errorDivEstudiante.style.display = 'none';
                errorDivEstudiante.innerHTML = '';
            }

            const brigadaId = formData.get('brigada_id');
            const carreraId = formData.get('carrera_id');

            if (!brigadaId || !carreraId) {
                mostrarErrorEstudiante('Por favor, selecciona una carrera válida.');
                return;
            }

            const url = `/brigada/${brigadaId}/${carreraId}/estudiante/agregar/`;
            const btnSubmit = form.querySelector('button[type="submit"]');

            try {
                if(btnSubmit) btnSubmit.disabled = true;

                const response = await fetch(url, { 
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value 
                    }
                });

                // LEER EL JSON DEL BACKEND
                const data = await response.json();

                if (data.success) {
                    // Si todo fue bien, recarga para ver el mensaje de éxito de Django
                    window.location.reload();
                } else {
                    // Si hubo error de validación, mostramos el mensaje y habilitamos el botón
                    mostrarErrorEstudiante(data.message || 'Error al guardar el estudiante.');
                    if (btnSubmit) btnSubmit.disabled = false;
                }

            } catch (error) {
                console.error("Error en Fetch:", error);
                mostrarErrorEstudiante('Error de conexión con el servidor. Revisa tu internet.');
                if (btnSubmit) btnSubmit.disabled = false;
            }
        });
    }
});