document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const Cpassword = document.getElementById('username').value.trim();
    const Npassword = document.getElementById('password').value.trim();

    if (Cpassword === '' || Npassword === '') {
        alert('Please fill in all fields.');
        return;
    }

    try {
        const response = await fetch(`${window.location.origin}/change_password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "Opassword": Cpassword, "Npassword": Npassword })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            window.location.href = "/logout"; 
        } else {
            alert(result.message); 
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Something went wrong. Please try again.');
    }
});

