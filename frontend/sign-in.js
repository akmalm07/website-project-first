const BACKEND_URL = 'https://no-licence-user-db-manager-runner-83470708869.us-central1.run.app';


document.getElementById('signin-form').addEventListener('submit', function(event) {
    event.preventDefault();
    handleLocalRegistration();
});

function handleLocalRegistration() {
    const email = document.getElementById("email-input").value;
    const password = document.getElementById("password-input").value;
    const name = document.getElementById("name-input").value;

    if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
        showNotification("Please enter a valid email address.", "error");
        return;
    }

    if (!validatePassword(password)) {
        showNotification("Password must be at least 8 characters long, include one uppercase, one lowercase, one number, and one special character.", "error");
        return;
    }

    fetch(`${BACKEND_URL}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, passcode: password }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Registration failed');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Registration successful:', data);
        localStorage.setItem("userId", data.userId);
        localStorage.setItem("userName", name);
        localStorage.setItem("userEmail", email);
        localStorage.setItem("authProvider", "local");
        hideModal();
        window.open('checkout.html', '_blank');
    })
    .catch(error => {
        console.error('Registration error:', error);
        showNotification(error.message, "error");
    });
}

function validatePassword(password) {
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}:"<>?;.,])(?=.{8,})/.test(password);
}

function hideModal() {
    document.getElementById("modal-content").style.display = "none";
}

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    const messageElem = document.getElementById('notification-message');
    messageElem.textContent = message;
    notification.classList.remove('success', 'error');
    notification.classList.add(type, 'show');
    setTimeout(() => notification.classList.remove('show'), 3000);
}
