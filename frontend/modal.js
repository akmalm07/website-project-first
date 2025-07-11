

const modal = document.getElementById("modal-content"); 
const signInBtn = document.getElementById("open-modal");
const closeModalBtn = document.getElementById("close-modal");


document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password-input');
    const togglePasswordButton = document.getElementById('toggle-password');
    const eyeIcon = document.getElementById('eye-icon');

    if (togglePasswordButton) {
        togglePasswordButton.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type');
            if (type === 'password') {
                passwordInput.setAttribute('type', 'text');
                eyeIcon.src = 'img/eye-open.png';
            } else {
                passwordInput.setAttribute('type', 'password');
                eyeIcon.src = 'img/eye-closed.png'; 
            }
        });
    }
});


signInBtn.addEventListener("click", (e) => {
  e.preventDefault();

  modal.classList.toggle("open");
});

closeModalBtn.addEventListener("click", () => {
  modal.classList.remove("open");
});


window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.remove("open");
  }
});


document.addEventListener('DOMContentLoaded', function() {
      const loginButton = document.getElementById('open-modal');

      if (localStorage.getItem('autoPressLogin') === 'true') {
        if (loginButton) {
          
          setTimeout( () => {
            loginButton.click(); 
          }, 1300);
         
          localStorage.removeItem('autoPressLogin');
        } else {
          console.log("Login button with ID 'open-modal' not found on this page.");
        }
      }
});


document.addEventListener('DOMContentLoaded', function() {
    const loginLink = document.getElementById('autoClickLoginLink');

    if (loginLink) {
      loginLink.addEventListener('click', function(event) {
        localStorage.setItem('autoPressLogin', 'true');
      });
    } else {
      console.log("Login link with ID 'autoClickLoginLink' not found on the current page.");
    }
});



document.addEventListener('DOMContentLoaded', function() {
      const signinButton = document.getElementById('open-modal');

      if (localStorage.getItem('autoPressSignin') === 'true') {
        if (signinButton) {
          setTimeout( () => {
            signinButton.click(); 
          }, 2000);
         
          localStorage.removeItem('autoPressSignin');
        } else {
          console.log("Login button with ID 'open-modal' not found on this page.");
        }
      }
});


document.addEventListener('DOMContentLoaded', function() {
    const signinLink = document.getElementById('autoClickSigninLink');

    if (signinLink) {
      signinLink.addEventListener('click', function(event) {
        localStorage.setItem('autoPressSignin', 'true');
      });
    } else {
      console.log("Login link with ID 'autoClickSigninLink' not found on the current page.");
    }
});