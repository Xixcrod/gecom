const modalProyecto = document.getElementById('proyectoModalManual');
const btnAbrir = document.getElementById('btnAbrirProyecto');
const btnCerrarX = document.getElementById('btnCerrarX');
const btnCancelar = document.getElementById('btnCancelar');
const formProyecto = document.getElementById('formProyecto'); 
const errorDivProyecto = document.getElementById('error-proyecto-ajax'); // <-- Nuevo contenedor

// 2. Función para ABRIR el modal
if (btnAbrir) {
    btnAbrir.addEventListener('click', () => {
        // Limpiamos los errores si vuelve a abrir el modal
        if (errorDivProyecto) {
            errorDivProyecto.style.display = 'none';
            errorDivProyecto.innerHTML = '';
        }
        modalProyecto.style.display = 'flex'; 
    });
}

// 3. Función para CERRAR el modal
const cerrar = () => {
    modalProyecto.style.display = 'none';
};

if (btnCerrarX) btnCerrarX.addEventListener('click', cerrar);
if (btnCancelar) btnCancelar.addEventListener('click', cerrar);

// 4. Cerrar al hacer clic fuera o presionar Escape
window.addEventListener('click', (e) => {
    if (e.target === modalProyecto) cerrar();
});

document.addEventListener('keydown', (e) => {
    if (e.key === "Escape" && modalProyecto.style.display === 'flex') cerrar();
});

// ======================================================
// 5. ENVÍO DEL FORMULARIO CON AJAX
// ======================================================

function mostrarErrorProyecto(mensaje) {
    if (!errorDivProyecto) return;
    errorDivProyecto.style.display = 'block';
    // Utilizamos tu clase error-modal-msg para mantener el estilo
    errorDivProyecto.innerHTML = `<div class="error-modal-msg"><i class="fas fa-exclamation-circle"></i> ${mensaje}</div>`;
}

if (formProyecto) {
    formProyecto.addEventListener('submit', function(e) {
        e.preventDefault(); 

        const formData = new FormData(this);
        const url = this.action;
        const btnGuardar = this.querySelector('.btn-guardar');

        // Ocultar errores previos antes de enviar
        if (errorDivProyecto) {
            errorDivProyecto.style.display = 'none';
            errorDivProyecto.innerHTML = '';
        }

        if(btnGuardar) btnGuardar.disabled = true;

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(async response => {
            const data = await response.json();
            
            if (data.success) {
                // ÉXITO: Django ya guardó el mensaje, recargamos la página.
                window.location.reload(); 
            } else {
                // ERROR: Mostramos el mensaje, NO recargamos, habilitamos el botón de nuevo.
                mostrarErrorProyecto(data.message || 'Ocurrió un error al guardar.');
                if (btnGuardar) btnGuardar.disabled = false;
            }
        })
        .catch(error => {
            // Este bloque captura errores críticos de red
            if (btnGuardar) btnGuardar.disabled = false;
            console.error('Error de red:', error);
            mostrarErrorProyecto('Error crítico al conectar con el servidor. Revisa tu conexión.');
        });
    });
}