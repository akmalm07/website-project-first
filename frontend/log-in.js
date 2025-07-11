const BACKEND_URL = '';


// Local login form submission handling
document.getElementById('login-form').addEventListener('submit', function(event) {
  event.preventDefault();
  handleLocalLogin();
});

function handleLocalLogin() {
  const email = document.getElementById("email-input").value;
  const password = document.getElementById("password-input").value;

  if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
    showNotification("Please enter a valid email address.", "error");
    return;
  }

  if (password.length < 8) {
    showNotification("Password must be at least 8 characters long.", "error");
    return;
  }

  fetch(`${BACKEND_URL}/users/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, passcode: password }),
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || 'Login failed');
      });
    }
    return response.json();
  })
  .then(data => {
    console.log('Login successful:', data);
    localStorage.setItem("userId", data.userId);
    localStorage.setItem("userName", data.name);
    localStorage.setItem("userEmail", email);
    localStorage.setItem("authProvider", "local");
    hideModal();
    if (data.subscribed == true)
     {
        window.open('exclusive_content_page.html', '_blank');
     }
     else
     { 
        window.open('checkout.html', '_blank');
     }
  })
  .catch(error => {
    console.error('Login error:', error);
    showNotification(error.message, "error");
  });
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
