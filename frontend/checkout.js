const BACKEND_URL = ''; //Provide your own 

window.onload = async () => {
    const userId = localStorage.getItem('userId'); // Replace with your actual way of getting the user ID

    if (!userId) {
        console.log("User ID not found.");
        return;
    }
};


// Function to display the notification
function showNotification(message, type) {
    const notification = document.getElementById('password-notification');
    const notificationMessage = document.getElementById('notification-message');

    notificationMessage.textContent = message; 
    notification.classList.remove('success', 'error');  
    notification.classList.add(type);  
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show'); 
    }, 3000);
}




/* Optional
// Stripe elements mounting
const cardNumber = elements.create("cardNumber", { style });
cardNumber.mount("#card-number");

const cardExpiry = elements.create("cardExpiry", { style });
cardExpiry.mount("#card-expiry");

const cardCvc = elements.create("cardCvc", { style });
cardCvc.mount("#card-cvc"); 
*/

document.getElementById("payment-button").addEventListener("click", async (e) => {
    e.preventDefault();

    // Open a blank window to avoid popup blockers
    const newWindow = window.open("about:blank");

    // Show a loading screen in the new window
    newWindow.document.write(`
      <html>
        <head>
          <title>Redirecting...</title>
          <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .loader {
              border: 8px solid #f3f3f3;
              border-radius: 50%;
              border-top: 8px solid #3498db;
              width: 60px;
              height: 60px;
              animation: spin 1s linear infinite;
              margin: 0 auto;
            }
            @keyframes spin {
              0% { transform: rotate(0deg);}
              100% { transform: rotate(360deg);}
            }
          </style>
        </head>
        <body>
          <h2>Redirecting to payment page...</h2>
          <div class="loader"></div>
        </body>
      </html>
    `);

    try {
        const userId = localStorage.getItem("userId");
        const email = localStorage.getItem("userEmail");

        const response = await fetch(`${BACKEND_URL}/users/${userId}/subscribe_url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': userId,
            },
            body: JSON.stringify({ email }),
        });

        const data = await response.json();

        if (response.ok && data.paymentLinkUrl) {
            newWindow.location.href = data.paymentLinkUrl;
        } else {
            newWindow.close();
            showNotification(`Failed to start checkout: ${data.error || 'Unknown error'}`, "error");
            alert(`Failed to start checkout: ${data.error || 'Unknown error'}`);
        }

    } catch (err) {
        newWindow.close();
        alert("Network error. Please try again.");
        console.error("Subscription error:", err);
    }
});




