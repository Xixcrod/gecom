// Esperamos a que el DOM cargue para leer los metadatos
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalDocumento');
    const form = document.getElementById('formDocumento');
    const errorAlerta = document.getElementById('errorAlerta');
    const modalTitulo = document.getElementById('modalTitulo');
    const btnConfirmar = document.getElementById('btnConfirmar');

    // Leemos el ID desde el atributo data del HTML
    const proyectoId = document.getElementById('metadata-proyecto').dataset.id;
    let tipoActual = "";

    // Definimos abrirModal en el objeto window para que el "onclick" del HTML lo vea
    window.abrirModal = function(slug, nombre, existe) {
        tipoActual = slug;
        modalTitulo.innerText = (existe === '1' ? 'Modificar ' : 'Subir ') + nombre;
        errorAlerta.style.display = 'none';
        form.reset();
        modal.style.display = 'flex';
    };

    window.cerrarModal = function() {
        modal.style.display = 'none';
    };

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        btnConfirmar.disabled = true;
        const textoOriginal = btnConfirmar.innerText;
        btnConfirmar.innerText = "Subiendo archivo...";
        errorAlerta.style.display = 'none';

        // URL dinámica usando el ID capturado
        const url = `/brigada/proyecto/${proyectoId}/subir-documento/${tipoActual}/`; 

        const formData = new FormData(form);

         const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // ÉXITO: Recargamos para que Django muestre el messages.success
                window.location.reload();
        } else {
            // ERROR CRÍTICO: El servidor falló (BD caída, etc.). Recargamos para ver el messages.error
            if (data.fatal_error) {
                window.location.reload();
                return;
            }

            // ERRORES DE VALIDACIÓN (Tamaño, formato, sin archivo)
            // Se muestran directamente en el modal
            errorAlerta.innerText = data.message;
            errorAlerta.style.display = 'block';
            
            // Restauramos el botón para que el usuario pueda intentar con otro archivo
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = "Reintentar Envío";
        }
        } catch (error) {
            errorAlerta.innerText = "Error crítico de conexión con el servidor.";
            errorAlerta.style.display = 'block';
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = textoOriginal;
        }
    });

    // Cerrar modal al hacer clic fuera de él
    window.onclick = function(event) {
        if (event.target == modal) cerrarModal();
    };
});