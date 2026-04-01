// 1. Función para ABRIR el modal y preparar los datos
function abrirModalEliminarBorrador(uuid, nombre) {
    // Ponemos el UUID y el nombre en el modal
    document.getElementById('uuidBorradorAEliminar').value = uuid;
    document.getElementById('nombreBorradorAEliminar').innerText = nombre;
    
    // Limpiamos errores anteriores por si acaso
    const alerta = document.getElementById('errorAlertaEliminar');
    alerta.style.display = 'none';
    alerta.innerText = '';
    
    // Mostramos la ventana
    document.getElementById('modalEliminarBorrador').style.display = 'flex';
}

// 2. Función para CERRAR el modal
function cerrarModalEliminarBorrador() {
    document.getElementById('modalEliminarBorrador').style.display = 'none';
}

// 3. Función para ELIMINAR en la base de datos (tu Fetch)
function procesarEliminacionBorrador() {
    const uuid = document.getElementById('uuidBorradorAEliminar').value;
    const alertaUI = document.getElementById('errorAlertaEliminar');
    const btnConfirmar = document.getElementById('btnConfirmarEliminar');

    if (!uuid) return;

    // Bloquear botón para no hacer doble clic
    btnConfirmar.disabled = true;
    btnConfirmar.innerText = "Eliminando...";

    // Buscamos el token ESPECÍFICAMENTE dentro del modal de eliminar
    const modalEliminar = document.getElementById('modalEliminarBorrador');
    const csrfToken = modalEliminar.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/brigada/draftbox/eliminar/${uuid}/`, {
        method: 'POST', 
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken, 
            'Content-Type': 'application/json' 
        }
    })
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta del servidor");
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("✅ " + data.message);
            cerrarModalEliminarBorrador();
            window.location.reload(); 
        } else {
            alertaUI.style.display = 'block';
            alertaUI.innerText = data.error || "No se pudo eliminar el borrador.";
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = "Sí, Eliminar";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alertaUI.style.display = 'block';
        alertaUI.innerText = "Error de conexión al intentar eliminar.";
        btnConfirmar.disabled = false;
        btnConfirmar.innerText = "Sí, Eliminar";
    });
}