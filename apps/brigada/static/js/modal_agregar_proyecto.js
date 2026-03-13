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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // --- CASO ÉXITO ---
                // 1. Mostramos el mensaje en el modal (opcional, por si tardan en dar aceptar)
                if (errorDiv) {
                    errorDiv.textContent = data.message;
                    errorDiv.style.color = "#28a745"; 
                    errorDiv.style.display = 'block';
                }

                // 2. LANZAMOS LA ALERTA: El navegador se detiene aquí.
                alert(data.message); 

                // 3. Cuando el usuario da clic en "Aceptar", se ejecuta la recarga:
                window.location.reload(); 

            } else {
                // --- CASO ERROR ---
                if (btnGuardar) btnGuardar.disabled = false; 
                
                if (errorDiv) {
                    errorDiv.textContent = data.message;
                    errorDiv.style.color = "#ff4444"; 
                    errorDiv.style.display = 'block';
                } else {
                    alert(data.message);
                }
            }
        })
        .catch(error => {
            if (btnGuardar) btnGuardar.disabled = false;
            console.error('Error:', error);
            alert('Error crítico al conectar con el servidor.');
        });
    });
}