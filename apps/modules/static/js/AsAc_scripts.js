// static/js/AsAc_scripts.js

// Función 1: Controla puramente lo visual (CSS y Tailwind)
function cambiarPestana(pestana) {
    const btnActivos = document.getElementById('btn-activos');
    const btnInactivos = document.getElementById('btn-inactivos');
    const listaActivos = document.getElementById('lista-activos');
    const listaInactivos = document.getElementById('lista-inactivos');

    // Validación de seguridad por si algún elemento no ha cargado
    if (!btnActivos || !btnInactivos || !listaActivos || !listaInactivos) return;

    if (pestana === 'activos') {
        // Mostrar lista activa
        listaActivos.classList.remove('hidden');
        listaActivos.classList.add('grid');
        
        // Ocultar lista inactiva
        listaInactivos.classList.remove('grid');
        listaInactivos.classList.add('hidden');
        
        // Estilos botón activos (Iluminado)
        btnActivos.classList.add('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
        btnActivos.classList.remove('bg-transparent', 'text-gray-600', 'hover:text-gray-800');
        
        // Estilos botón inactivos (Apagado)
        btnInactivos.classList.add('bg-transparent', 'text-gray-600', 'hover:text-gray-800');
        btnInactivos.classList.remove('bg-white', 'text-[#8b5cf6]', 'shadow-sm');

    } else {
        // Mostrar lista inactiva
        listaInactivos.classList.remove('hidden');
        listaInactivos.classList.add('grid');
        
        // Ocultar lista activa
        listaActivos.classList.remove('grid');
        listaActivos.classList.add('hidden');
        
        // Estilos botón inactivos (Iluminado)
        btnInactivos.classList.add('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
        btnInactivos.classList.remove('bg-transparent', 'text-gray-600', 'hover:text-gray-800');
        
        // Estilos botón activos (Apagado)
        btnActivos.classList.add('bg-transparent', 'text-gray-600', 'hover:text-gray-800');
        btnActivos.classList.remove('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
    }
}

// Función 2: Controla la lógica de datos, formularios y URL
function irAPestana(pestana) {
    // Actualiza el buscador
    const inputSearch = document.getElementById('search-tab-input');
    if (inputSearch) inputSearch.value = pestana;
    
    // Actualiza los modales
    document.querySelectorAll('.tab_actual_input').forEach(input => {
        input.value = pestana;
    });

    // Ejecuta el cambio visual
    cambiarPestana(pestana);
    
    // Guarda el estado en la URL silenciosamente
    const url = new URL(window.location);
    url.searchParams.set('tab', pestana);
    window.history.pushState({}, '', url);
}

// Inicializador: Se ejecuta apenas carga la página
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // TRUCO: Como el JS externo no entiende de Django, buscamos el input oculto 
    // de la barra de búsqueda (que sí fue renderizado por Django) y leemos su valor.
    const inputSearch = document.getElementById('search-tab-input');
    const valorDjango = inputSearch ? inputSearch.value : 'activos';

    // Lee la URL primero, si no hay nada en la URL, usa la variable de Django
    const tabInicial = urlParams.get('tab') || valorDjango;
    irAPestana(tabInicial);
});