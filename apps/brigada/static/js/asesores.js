// --- UTILIDADES ---
const getCsrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]').value;

const getApiUrls = () => {
    const container = document.getElementById('card-asesores');
    return {
        academico: container.dataset.urlAcademico,
        comunitario: container.dataset.urlComunitario
    };
};

// --- LÓGICA ASESOR ACADÉMICO ---
// Abrir y cerrar modal de asignar asesor académico
function abrirModalAsignarAcademico() {
    document.getElementById('modalAsignarAcademico').style.display = 'flex';
    document.getElementById('inputBusquedaAcademico').focus();
}

function cerrarModalAsignarAcademico() {
    document.getElementById('modalAsignarAcademico').style.display = 'none';
}

// Lógica de filtrado en tiempo real
function filtrarAsesores() {
    const input = document.getElementById('inputBusquedaAcademico').value.toLowerCase();
    const items = document.querySelectorAll('.item-asesor');
    
    items.forEach(item => {
        const info = item.getAttribute('data-info').toLowerCase();
        if (info.includes(input)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Selección de asesor académico
function seleccionarAsesor(elemento) {
    // Quitar selección previa
    document.querySelectorAll('.item-asesor').forEach(i => i.classList.remove('seleccionado'));
    
    // Marcar nuevo seleccionado
    elemento.classList.add('seleccionado');
    const id = elemento.getAttribute('data-id');
    document.getElementById('asesor_seleccionado_id').value = id;
    
    // Habilitar botón de guardar
    document.getElementById('btnGuardarAcademico').disabled = false;
}

// Función para enviar los datos del asesor académico seleccionado al servidor
function guardarAcademicoNuevo(brigadaId) {
    const asesorId = document.getElementById('asesor_seleccionado_id').value;
    const { academico: url } = getApiUrls();

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ asesor_base_id: asesorId })
    })
    .then(res => location.reload())
    .catch(err => alert("Error de comunicación con el servidor."));
}

// --- LÓGICA ASESOR COMUNITARIO ---
function abrirModalComunitario(id, nombres, apellidos, cedula, telefono, correo) {
    document.getElementById('com_id').value = id || '';
    document.getElementById('com_nombres').value = nombres || '';
    document.getElementById('com_apellidos').value = apellidos || '';
    document.getElementById('com_cedula').value = cedula || '';
    document.getElementById('com_telefono').value = telefono || '';
    document.getElementById('com_correo').value = correo || '';
    
    document.getElementById('modal-titulo').innerText = id ? 'Editar Asesor Comunitario' : 'Nuevo Asesor Comunitario';
    
    const modal = document.getElementById('modalComunitario');
    modal.style.display = 'flex';
}

function cerrarModalComunitario() {
    document.getElementById('modalComunitario').style.display = 'none';
}

function guardarComunitario(brigadaId) {
    const payload = {
        asesor_id: document.getElementById('com_id').value,
        nombres: document.getElementById('com_nombres').value,
        apellidos: document.getElementById('com_apellidos').value,
        cedula: document.getElementById('com_cedula').value,
        telefono: document.getElementById('com_telefono').value,
        correo: document.getElementById('com_correo').value
    };

    // Validación simple
    if (!payload.nombres || !payload.cedula) {
        alert("Nombres y Cédula son obligatorios.");
        return;
    }

    const { comunitario: url } = getApiUrls();

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
    })
    .then(res => {
        // Recargamos la página sin importar si es 200, 400 o 500.
        // Django habrá guardado el mensaje (success o error) en la sesión.
        location.reload();
    })
    .catch(err => {
        console.error("Error crítico de red:", err);
        alert("Error de conexión con el servidor.");
    });
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('modalComunitario');
    if (event.target === modal) {
        cerrarModalComunitario();
    }
};