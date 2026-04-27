// 1. Referenciamos los elementos del DOM
const modalProyecto = document.getElementById('proyectoModalManual');
const btnAbrir = document.getElementById('btnAbrirProyecto');
const btnCerrarX = document.getElementById('btnCerrarX');
const btnCancelar = document.getElementById('btnCancelar');
const formProyecto = document.getElementById('formProyecto'); 
const errorDiv = document.getElementById('error-proyecto'); 

// 2. Función para ABRIR el modal
if (btnAbrir) {
    btnAbrir.addEventListener('click', () => {
        modalProyecto.style.display = 'flex'; 
    });
}

// 3. Función para CERRAR el modal
const cerrar = () => {
    modalProyecto.style.display = 'none';
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
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
// 5. ENVÍO DEL FORMULARIO CON ESPERA DE "ACEPTAR"
// ======================================================
if (formProyecto) {
    formProyecto.addEventListener('submit', function(e) {
        e.preventDefault(); 

        const formData = new FormData(this);
        const url = this.action;
        const btnGuardar = this.querySelector('.btn-guardar');

        if(btnGuardar) btnGuardar.disabled = true;

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            window.location.reload(); 
        })
        .catch(error => {
            // Este bloque captura errores de red
            // (ej. el usuario se quedó sin internet o el servidor se apagó por completo)
            if (btnGuardar) btnGuardar.disabled = false;
            console.error('Error de red:', error);
            alert('Error crítico al conectar con el servidor. Revisa tu conexión.');
        });
    });
}