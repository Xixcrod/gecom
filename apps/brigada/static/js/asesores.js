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
function toggleSelectorAcademico() {
    const div = document.getElementById('selector-academico-div');
    const info = document.getElementById('info-academico');
    
    if (div.style.display === 'none') {
        div.style.display = 'block';
        if (info) info.style.display = 'none';
    } else {
        div.style.display = 'none';
        if (info) info.style.display = 'block';
    }
}

function guardarAcademico(brigadaId) {
    const asesorId = document.getElementById('select-academico').value;
    if (!asesorId) {
        alert('Por favor, selecciona un asesor académico activo.');
        return;
    }

    const { academico: url } = getApiUrls();

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ asesor_base_id: asesorId })
    })
    .then(res => {
        // Independientemente de si es success o error, recargamos.
        // El backend ya se encargó de poner el mensaje en la cola de Django.
        location.reload();
    })
    .catch(err => {
        console.error("Error en la petición:", err);
        // Este alert solo aparece si hay un error de red (el servidor no responde)
        alert("Error crítico de comunicación con el servidor.");
    });
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