// 1. Referenciamos los elementos del DOM
    const modalProyecto = document.getElementById('proyectoModalManual');
    const btnAbrir = document.getElementById('btnAbrirProyecto');
    const btnCerrarX = document.getElementById('btnCerrarX');
    const btnCancelar = document.getElementById('btnCancelar');

    // 2. Evento para ABRIR el modal
    if (btnAbrir) {
        btnAbrir.addEventListener('click', () => {
            // .showModal() es el comando nativo para mostrar el dialog
            modalProyecto.showModal(); 
        });
    }

    // 3. Eventos para CERRAR el modal
    const cerrar = () => modalProyecto.close();

    if (btnCerrarX) btnCerrarX.addEventListener('click', cerrar);
    if (btnCancelar) btnCancelar.addEventListener('click', cerrar);

    // 4. (Opcional) Cerrar si el usuario hace clic fuera de la cajita blanca
    modalProyecto.addEventListener('click', (e) => {
        if (e.target === modalProyecto) cerrar();
    });