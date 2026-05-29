// static/js/periodo_scripts.js

// ==========================================
// 1. LÓGICA DE VENTANAS MODALES
// ==========================================

function abrirModalPeriodo(id = '', desdeSem = 'I', desdeAnio = '', hastaSem = 'II', hastaAnio = '') {
    const modal = document.getElementById('modalPeriodo');
    const titulo = document.getElementById('tituloModalPeriodo');
    
    // Inyectar los valores recibidos de Django en los inputs del formulario
    document.getElementById('periodo_id').value = id;
    document.getElementById('desde_semestre').value = desdeSem;
    document.getElementById('desde_anio').value = desdeAnio;
    document.getElementById('hasta_semestre').value = hastaSem;
    document.getElementById('hasta_anio').value = hastaAnio;

    // Cambiar dinámicamente el título según la acción
    if (id) {
        titulo.innerText = 'Modificar Periodo';
    } else {
        titulo.innerText = 'Añadir Nuevo Periodo';
        
        // Auto-completar años basándonos en el año actual (Opcional, mejora UX)
        const anioActual = new Date().getFullYear();
        document.getElementById('desde_anio').value = anioActual;
        document.getElementById('hasta_anio').value = anioActual;
    }

    // Mostrar modal con display flex (como en tus brigadas)
    modal.style.display = 'flex';
}

function cerrarModalPeriodo() {
    const modal = document.getElementById('modalPeriodo');
    modal.style.display = 'none';
    document.getElementById('formPeriodo').reset(); // Limpia los datos
}

// Cierra el modal si el usuario hace clic fuera de la tarjeta blanca (en el fondo oscuro)
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modalPeriodo');
    if (event.target === modal) {
        cerrarModalPeriodo();
    }
});


// ==========================================
// 2. LÓGICA DE PAGINACIÓN ANIMADA (AJAX)
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    
    document.addEventListener('click', function(e) {
        // Buscamos si el clic provino de un enlace de paginación
        const link = e.target.closest('.link-paginador');
        if (!link) return;

        e.preventDefault();
        const url = link.getAttribute('href');
        const grid = document.getElementById('grid-periodos');

        if (!grid) return;

        // --- Animación de Salida ---
        grid.classList.remove('translate-x-0', 'opacity-100');
        grid.classList.add('-translate-x-10', 'opacity-0');

        // Esperamos la animación (300ms)
        setTimeout(() => {
            fetch(url)
            .then(respuesta => respuesta.text())
            .then(htmlStr => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlStr, 'text/html');

                const contenedorActual = document.getElementById('contenedor-periodos');
                const nuevoContenedor = doc.getElementById('contenedor-periodos');
                
                if (contenedorActual && nuevoContenedor) {
                    // Reemplazamos el HTML
                    contenedorActual.innerHTML = nuevoContenedor.innerHTML;
                    
                    const nuevoGrid = document.getElementById('grid-periodos');
                    if (nuevoGrid) {
                        // Preparamos para animación de entrada invisiblemente a la derecha
                        nuevoGrid.style.transition = 'none';
                        nuevoGrid.classList.remove('translate-x-0', 'opacity-100');
                        nuevoGrid.classList.add('translate-x-10', 'opacity-0');

                        // Forzamos al navegador a procesar el cambio (Reflow)
                        void nuevoGrid.offsetWidth; 

                        // --- Animación de Entrada ---
                        nuevoGrid.style.transition = '';
                        nuevoGrid.classList.remove('translate-x-10', 'opacity-0');
                        nuevoGrid.classList.add('translate-x-0', 'opacity-100');
                    }

                    // Actualizamos la URL en el navegador silenciosamente
                    window.history.pushState({}, '', url);
                }
            })
            .catch(error => console.error('Error al cargar la página:', error));
        }, 300);
    });

    // Permite que funcione el botón de ir "atrás" en el navegador correctamente
    window.addEventListener('popstate', function() {
        window.location.reload();
    });
});