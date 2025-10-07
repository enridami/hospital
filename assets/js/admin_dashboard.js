function editUser(userId) {
    if (!userId) {
        alert('Error: ID de usuario no válido');
        return;
    }
    window.location.href = `/admin/users/edit/${userId}/`;
}

function toggleUserStatus(userId) {
    if (!userId) {
        alert('Error: ID de usuario no válido');
        return;
    }
    
    if (confirm('¿Está seguro de cambiar el estado de este usuario?')) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            alert('Error: Token CSRF no encontrado');
            return;
        }
        
        fetch(`/admin-dashboard/users/toggle-status/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken.value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al cambiar el estado del usuario');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al procesar la solicitud');
        });
    }
}