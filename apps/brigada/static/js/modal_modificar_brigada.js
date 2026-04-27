function abrirModalModificar(brigadaId, nombreActual) {
    const modal = document.getElementById('customModal');
    document.getElementById('hiddenBrigadaId').value = brigadaId;
    document.getElementById('inputNuevoNombre').value = nombreActual;
    document.getElementById('error-msg').style.display = 'none';
    
    modal.style.display = 'flex'; // Mostramos el modal
}

function cerrarModal() {
    document.getElementById('customModal').style.display = 'none';
}

function enviarModificacion() {
    const brigadaId = document.getElementById('hiddenBrigadaId').value;
    const nuevoNombre = document.getElementById('inputNuevoNombre').value.trim();
    const errorDiv = document.getElementById('error-msg');

    // 1. Validación en Cliente: Solo números enteros (Regex)
    if (!/^\d+$/.test(nuevoNombre)) {
        errorDiv.textContent = "Error: El nombre debe ser solo números enteros.";
        errorDiv.style.display = 'block';
        return;
    }

    // 2. Petición AJAX
    fetch(`/brigada/brigada/${brigadaId}/brigada/modificar/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ nombre: nuevoNombre })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    })
    .catch(error => {
        errorDiv.textContent = "Error de conexión con el servidor.";
        errorDiv.style.display = 'block';
    });
}

// Función para obtener el CSRF Token (necesaria para Django)
function getCookie(name) {
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
}