document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('estudiante-modal');
    const btnAbrir = document.getElementById('estudiante-btn-nuevo');
    const btnCerrar = document.getElementById('estudiante-btn-cerrar');
    const form = document.getElementById('estudiante-form');
    const divError = document.getElementById('estudiante-error');
    const listaEstudiantes = document.getElementById('estudiante-lista');

    // --- Manejo del Modal ---
    btnAbrir.addEventListener('click', () => {
        modal.style.display = 'flex';
        divError.style.display = 'none'; 
        form.reset(); 
    });

    btnCerrar.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // --- Envío del formulario vía Fetch ---
    form.addEventListener('submit', async function(e) {
        e.preventDefault(); 

        const formData = new FormData(form);
        divError.style.display = 'none';

        // DEBUG: Revisa esto en la consola (F12)
        const brigadaId = formData.get('brigada_id');
        const carreraId = formData.get('carrera_id');

        // Si alguno es null o vacío, lanzamos el mensaje de error
        if (!brigadaId || brigadaId === "None" || !carreraId) {
            divError.textContent = 'Asegúrate de seleccionar una carrera válida.';
            divError.style.display = 'block';
            return;
        }

        const url = `/brigada/${brigadaId}/${carreraId}/estudiante/agregar/`;
        console.log("Enviando a URL:", url);

        try {
            // Deshabilitar botón para evitar doble clic
            const btnSubmit = form.querySelector('button[type="submit"]');
            if(btnSubmit) btnSubmit.disabled = true;

            const response = await fetch(url, { 
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    // Importante: No olvides el CSRF Token si no está en el FormData
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value 
                }
            });

            const data = await response.json();

            if (!response.ok || !data.exito) {
                // CASO ERROR: Mostramos el mensaje en el modal sin cerrarlo
                divError.textContent = data.mensaje || 'Error al guardar.';
                divError.style.display = 'block';
                if(btnSubmit) btnSubmit.disabled = false;
            } else {
                // CASO ÉXITO: Cerramos y recargamos para que aparezca el mensaje de Django
                modal.style.display = 'none';
                window.location.reload(); 
            }

        } catch (error) {
            divError.textContent = 'Error de conexión con el servidor.';
            divError.style.display = 'block';
            const btnSubmit = form.querySelector('button[type="submit"]');
            if(btnSubmit) btnSubmit.disabled = false;
        }
    });
});