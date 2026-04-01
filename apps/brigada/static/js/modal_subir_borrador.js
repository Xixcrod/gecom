function abrirModalBorrador() {
    document.getElementById('modalBorrador').style.display = 'flex';
}

function cerrarModalBorrador() {
    document.getElementById('modalBorrador').style.display = 'none';
    document.getElementById('formBorrador').reset();
    const alerta = document.getElementById('errorAlertaBorrador');
    alerta.style.display = 'none';
    alerta.innerText = '';
}

document.getElementById('formBorrador').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const alertaUI = document.getElementById('errorAlertaBorrador');
    const btnSubmit = this.querySelector('button[type="submit"]');

    // Bloquear botón para evitar dobles envíos
    btnSubmit.disabled = true;
    btnSubmit.innerText = "Subiendo...";

    // Asegúrate de poner la URL correcta que configuraste en urls.py para tu vista
    fetch(`/brigada/draftbox/subir/`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(response => {
            if (!response.ok) throw new Error("Error interno del servidor");
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alertaUI.style.display = 'block';
                alertaUI.style.color = 'green';
                alertaUI.innerText = data.message;

                alert("✅ " + data.message);
                cerrarModalBorrador();
                window.location.reload(); // Recargamos para ver el nuevo archivo en la lista
            } else {
                alertaUI.style.display = 'block';
                alertaUI.style.color = 'red';
                alertaUI.innerText = data.error;
                btnSubmit.disabled = false;
                btnSubmit.innerText = "Guardar Borrador";
            }
        })
        .catch(error => {
            alertaUI.style.display = 'block';
            alertaUI.style.color = 'red';
            alertaUI.innerText = "Hubo un problema de conexión con el servidor.";
            btnSubmit.disabled = false;
            btnSubmit.innerText = "Guardar Borrador";
        });
});