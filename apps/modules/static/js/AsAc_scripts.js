// static/js/AsAc_scripts.js

function cambiarPestana(pestana) {
    const btnActivos = document.getElementById('btn-activos');
    const btnInactivos = document.getElementById('btn-inactivos');
    const listaActivos = document.getElementById('lista-activos');
    const listaInactivos = document.getElementById('lista-inactivos');

    if (pestana === 'activos') {
        // 1. Mostrar lista activa (Quitamos hidden, agregamos grid)
        listaActivos.classList.remove('hidden');
        listaActivos.classList.add('grid');
        
        // 2. Ocultar lista inactiva (Quitamos grid, agregamos hidden para evitar el conflicto)
        listaInactivos.classList.remove('grid');
        listaInactivos.classList.add('hidden');
        
        // Estilos botón activos (Iluminado)
        btnActivos.classList.add('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
        btnActivos.classList.remove('bg-transparent', 'text-gray-500', 'hover:text-gray-700');
        
        // Estilos botón inactivos (Apagado)
        btnInactivos.classList.add('bg-transparent', 'text-gray-500', 'hover:text-gray-700');
        btnInactivos.classList.remove('bg-white', 'text-[#8b5cf6]', 'shadow-sm');

    } else {
        // 1. Mostrar lista inactiva (Quitamos hidden, agregamos grid)
        listaInactivos.classList.remove('hidden');
        listaInactivos.classList.add('grid');
        
        // 2. Ocultar lista activa (Quitamos grid, agregamos hidden)
        listaActivos.classList.remove('grid');
        listaActivos.classList.add('hidden');
        
        // Estilos botón inactivos (Iluminado)
        btnInactivos.classList.add('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
        btnInactivos.classList.remove('bg-transparent', 'text-gray-500', 'hover:text-gray-700');
        
        // Estilos botón activos (Apagado)
        btnActivos.classList.add('bg-transparent', 'text-gray-500', 'hover:text-gray-700');
        btnActivos.classList.remove('bg-white', 'text-[#8b5cf6]', 'shadow-sm');
    }
}