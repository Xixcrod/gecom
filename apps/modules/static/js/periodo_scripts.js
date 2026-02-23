// static/js/periodo_scripts.js

document.addEventListener('DOMContentLoaded', () => {
    
    // Escuchamos los clics en todo el documento
    document.addEventListener('click', function(e) {
        // Buscamos si hicimos clic en un enlace del paginador
        const link = e.target.closest('.link-paginador');
        if (!link) return;

        // Evitamos que la página se recargue bruscamente
        e.preventDefault();
        const url = link.getAttribute('href');
        const grid = document.getElementById('grid-periodos');

        if (!grid) return;

        // 1. Animación de Salida: Deslizamos el grid actual hacia la izquierda y lo desvanecemos
        grid.classList.remove('translate-x-0', 'opacity-100');
        grid.classList.add('-translate-x-10', 'opacity-0');

        // 2. Esperamos que termine la animación (300ms) para traer la nueva página
        setTimeout(() => {
            fetch(url)
            .then(respuesta => respuesta.text())
            .then(htmlStr => {
                // Convertimos el texto HTML en elementos manejables
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlStr, 'text/html');

                // 3. Extraemos el nuevo contenedor completo desde la respuesta y lo reemplazamos
                const contenedorActual = document.getElementById('contenedor-periodos');
                const nuevoContenedor = doc.getElementById('contenedor-periodos');
                
                if (contenedorActual && nuevoContenedor) {
                    contenedorActual.innerHTML = nuevoContenedor.innerHTML;

                    // 4. Preparamos el nuevo Grid para la animación de entrada
                    const nuevoGrid = document.getElementById('grid-periodos');
                    
                    // Quitamos la transición momentáneamente para moverlo a la derecha invisiblemente
                    nuevoGrid.style.transition = 'none';
                    nuevoGrid.classList.remove('translate-x-0', 'opacity-100');
                    nuevoGrid.classList.add('translate-x-10', 'opacity-0');

                    // Forzamos al navegador a aplicar los cambios inmediatos (Reflow)
                    void nuevoGrid.offsetWidth;

                    // 5. Devolvemos la transición y animamos hacia el centro
                    nuevoGrid.style.transition = '';
                    nuevoGrid.classList.remove('translate-x-10', 'opacity-0');
                    nuevoGrid.classList.add('translate-x-0', 'opacity-100');

                    // 6. Actualizamos la URL en el navegador sin recargar
                    window.history.pushState({}, '', url);
                }
            })
            .catch(error => console.error('Error al cargar la página:', error));
        }, 300);
    });

    // Este evento asegura que el botón de "Atrás" del navegador funcione con nuestra animación
    window.addEventListener('popstate', function() {
        window.location.reload();
    });
});