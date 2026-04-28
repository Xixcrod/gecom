// 1. Función para ABRIR el modal y preparar los datos
function abrirModalEliminarBorrador(uuid, nombre) {
    document.getElementById('uuidBorradorAEliminar').value = uuid;
    document.getElementById('nombreBorradorAEliminar').innerText = nombre;
    
    const alerta = document.getElementById('errorAlertaEliminar');
    if (alerta) {
        alerta.style.display = 'none';
        alerta.innerText = '';
    }
    
    document.getElementById('modalEliminarBorrador').style.display = 'flex';
}

// 2. Función para CERRAR el modal
function cerrarModalEliminarBorrador() {
    document.getElementById('modalEliminarBorrador').style.display = 'none';
}

// 3. Función para ELIMINAR en la base de datos (Fetch con estándar moderno)
async function procesarEliminacionBorrador() {
    const uuid = document.getElementById('uuidBorradorAEliminar').value;
    const alertaUI = document.getElementById('errorAlertaEliminar');
    const btnConfirmar = document.getElementById('btnConfirmarEliminar');

    if (!uuid) return;

    // Estado de carga
    btnConfirmar.disabled = true;
    btnConfirmar.innerText = "Eliminando...";

    // Buscamos el token CSRF dentro del modal
    const modalEliminar = document.getElementById('modalEliminarBorrador');
    const csrfToken = modalEliminar.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch(`/brigada/draftbox/eliminar/${uuid}/`, {
            method: 'POST', 
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // ÉXITO: Recargamos para que Django muestre el message.success
            // Quitamos el alert() para que la experiencia sea más fluida
            window.location.reload();
        } else {
            // ERROR CRÍTICO (500): Recargamos para ver el message.error
            if (data.fatal_error) {
                window.location.reload();
                return;
            }

            // ERROR DE VALIDACIÓN O LÓGICO: Mostramos en el modal
            if (alertaUI) {
                alertaUI.style.display = 'block';
                alertaUI.style.color = '#dc3545'; // Rojo
                alertaUI.innerText = data.message || "No se pudo eliminar el borrador.";
            }
            
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = "Sí, Eliminar";
        }
    } catch (error) {
        console.error("Error:", error);
        if (alertaUI) {
            alertaUI.style.display = 'block';
            alertaUI.innerText = "Error de conexión al intentar eliminar.";
        }
        btnConfirmar.disabled = false;
        btnConfirmar.innerText = "Sí, Eliminar";
    }
}