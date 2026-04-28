function abrirModalBorrador() {
    document.getElementById('modalBorrador').style.display = 'flex';
}

function cerrarModalBorrador() {
    const modal = document.getElementById('modalBorrador');
    const form = document.getElementById('formBorrador');
    const alerta = document.getElementById('errorAlertaBorrador');
    
    modal.style.display = 'none';
    form.reset();
    alerta.style.display = 'none';
    alerta.innerText = '';
}

// Función auxiliar para obtener el CSRF (puedes tenerla en un archivo global)
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

document.getElementById('formBorrador').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const alertaUI = document.getElementById('errorAlertaBorrador');
    const btnSubmit = this.querySelector('button[type="submit"]');
    const textoOriginal = btnSubmit.innerText;

    // UI Initial State
    btnSubmit.disabled = true;
    btnSubmit.innerText = "Subiendo archivo...";
    alertaUI.style.display = 'none';

    try {
        const response = await fetch(`/brigada/draftbox/subir/`, {
            method: 'POST',
            body: formData,
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Caso Éxito: Recargamos para que Django muestre el messages.success
            window.location.reload();
        } else {
            // Caso Error Fatal (500): Recargamos para ver el messages.error
            if (data.fatal_error) {
                window.location.reload();
                return;
            }

            // Caso Error de Validación (400): Se queda en el modal
            alertaUI.style.display = 'block';
            alertaUI.style.color = '#dc3545'; // Rojo estándar
            alertaUI.innerText = data.message || "Error al procesar el archivo.";
            
            btnSubmit.disabled = false;
            btnSubmit.innerText = "Reintentar Guardar";
        }

    } catch (error) {
        console.error("Error:", error);
        alertaUI.style.display = 'block';
        alertaUI.innerText = "Error de conexión con el servidor.";
        btnSubmit.disabled = false;
        btnSubmit.innerText = textoOriginal;
    }
});