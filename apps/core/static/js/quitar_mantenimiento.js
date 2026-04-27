    const checkInterval = setInterval(async () => {
        try {
            // Ajusta la URL según tu urls.py
            const response = await fetch('/backup/restore_status/');
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(checkInterval);
                // Redirigir al login
                window.location.href = '/'; 
            }
        } catch (error) {
            console.log("Esperando a que el servidor reinicie...");
        }
    }, 3000); // Revisa cada 3 segundos