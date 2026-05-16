// modal_brigada.js
function toggleModal(show) {
    const modal = document.getElementById('modalBrigada');
    if (!modal) return;
    
    modal.style.display = show ? 'flex' : 'none';
    
    if (show) {
        const input = modal.querySelector('input[name="nombre"]');
        if (input) input.focus();
        
        // Limpiar errores previos al abrir
        const errorContainer = document.getElementById('error-brigada-ajax');
        if (errorContainer) {
            errorContainer.innerHTML = '';
            errorContainer.style.display = 'none';
        }
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formNuevaBrigada');
    const errorContainer = document.getElementById('error-brigada-ajax');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault(); // <--- CRÍTICO: Esto evita la "ventana negra"


            const formData = new FormData(form);
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (data.success) {
                    location.reload(); 
                } else {

                    errorContainer.innerHTML = '';
                    errorContainer.style.display = 'block';
                    
                    // Ajuste según el formato JSON que te mostró la imagen:
                    for (const campo in data.errors) {
                        data.errors[campo].forEach(err => {
                            const div = document.createElement('div');
                            div.className = 'error-modal-msg'; 
                            div.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${err.message}`;
                            errorContainer.appendChild(div);
                        });
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }
});

