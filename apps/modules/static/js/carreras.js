// apps/modules/static/js/carreras.js

function abrirModalCarrera(id = '', nombre = '') {
    const modal = document.getElementById('modalCarrera');
    const titulo = document.getElementById('tituloModalCarrera');
    
    // Asignar los valores a los inputs que tu backend espera
    document.getElementById('carrera_id').value = id;
    document.getElementById('nombre_carrera').value = nombre;

    // Lógica clave para tu backend: 'accion'
    const inputAccion = document.getElementById('input_accion');
    
    if (id !== '') {
        titulo.innerText = 'Modificar Carrera';
        inputAccion.value = 'editar'; // Coincide con tu condicional en procesar_formulario_carrera
    } else {
        titulo.innerText = 'Añadir Nueva Carrera';
        inputAccion.value = 'crear';  // Coincide con tu condicional en procesar_formulario_carrera
        document.getElementById('formCarrera').reset(); // Limpiamos campos si es nuevo
    }

    modal.style.display = 'flex';
}

function cerrarModalCarrera() {
    document.getElementById('modalCarrera').style.display = 'none';
}

// Cierra al hacer clic fuera del modal
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modalCarrera');
    if (event.target === modal) cerrarModalCarrera();
});