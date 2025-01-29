document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (username === '' || password === '') {
        alert('Please fill in all fields.');
        return;
    }

    try {
        const response = await fetch(`${window.location.origin}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "username": username, "password": password })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            window.location.href = "/dashboard"; 
        } else {
            alert(result.message); 
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Something went wrong. Please try again.');
    }
});

