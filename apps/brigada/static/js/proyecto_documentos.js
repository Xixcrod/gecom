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
        modal.style.display = 'block';
    };

    window.cerrarModal = function() {
        modal.style.display = 'none';
    };

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        btnConfirmar.disabled = true;
        const textoOriginal = btnConfirmar.innerText;
        btnConfirmar.innerText = "Validando PDF...";
        errorAlerta.style.display = 'none';

        // URL dinámica usando el ID capturado
        const url = `/brigada/proyecto/${proyectoId}/subir-documento/${tipoActual}/`; 

        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const resultado = await response.text();

            if (response.ok) {
                window.location.reload();
            } else {
                // Mostramos el error de validación del backend
                errorAlerta.innerText = resultado.replace("Error de validación: ", "");
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

    // Cerrar modal al hacer clic fuera de él
    window.onclick = function(event) {
        if (event.target == modal) cerrarModal();
    };
});