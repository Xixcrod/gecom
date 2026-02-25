setTimeout(() => {
            const toasts = document.querySelectorAll('.toast .alert');
            toasts.forEach(t => {
                t.style.opacity = '0';
                setTimeout(() => t.parentElement.remove(), 500); // Dar tiempo a la animación css
            });
        }, 7000);