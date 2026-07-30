document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalDocumento');
    const form = document.getElementById('formDocumento');
    const errorAlerta = document.getElementById('errorAlerta');
    const modalTitulo = document.getElementById('modalTitulo');
    const btnConfirmar = document.getElementById('btnConfirmar');

    const estudianteId = document.getElementById('metadata-estudiante').dataset.id;
    let tipoActual = "";

    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    window.abrirModal = function(nombre, existe) {
        tipoActual = nombre;
        modalTitulo.innerText = (existe === '1' ? 'Modificar ' : 'Subir ') + nombre;
        errorAlerta.style.display = 'none';
        form.reset();
        modal.style.display = 'block';
    };

    window.cerrarModal = function() {
        modal.style.display = 'none';
    };

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        btnConfirmar.disabled = true;
        const textoOriginal = btnConfirmar.innerText;
        btnConfirmar.innerText = "Validando Archivo...";
        errorAlerta.style.display = 'none';

        const url = `/brigada/estudiante/${estudianteId}/subir-certificado/`; 
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken') 
                }
            });

            // 1. Convertimos la respuesta a JSON
            const data = await response.json();

            if (response.ok && data.success) {
                // ÉXITO: Recargamos para que Django renderice el messages.success
                window.location.reload();
            } else {
                // ERROR CRÍTICO: Recargamos para que Django renderice el messages.error
                if (data.fatal_error) {
                    window.location.reload();
                    return;
                }

                // ERRORES DE VALIDACIÓN: Se muestran en el modal (data.message)
                errorAlerta.innerText = data.message;
                errorAlerta.style.display = 'block';
                
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

    window.onclick = function(event) {
        if (event.target == modal) cerrarModal();
    };
});