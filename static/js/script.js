// DOM Elements for Modal
const authModal = document.getElementById('auth-modal');
const closeModal = document.querySelector('.close');
const authForm = document.getElementById('auth-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirm-password');
const registerButton = document.getElementById('register-btn');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const confirmPasswordGroup = document.getElementById('confirm-password-group');
const logoutButton = document.getElementById('logout-btn');

// Show the modal on page load
window.onload = function () {
    authModal.style.display = 'block';
};

// Close modal when user clicks on <span> (x)
closeModal.onclick = function () {
    authModal.style.display = 'none';
};

// Close modal when user clicks anywhere outside of the modal
window.onclick = function (event) {
    if (event.target === authModal) {
        authModal.style.display = 'none';
    }
};

// Email validation function
function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Basic regex for email validation
    return emailPattern.test(email);
}

// Password strength validation function
function isStrongPassword(password) {
    const minLength = 8; // Minimum length of 8 characters
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return (
        password.length >= minLength &&
        hasUpperCase &&
        hasLowerCase &&
        hasNumbers &&
        hasSpecialChars
    );
}

// Function to update the UI for email validation feedback
function updateEmailValidationUI() {
    const email = usernameInput.value;
    const feedbackElement = document.getElementById('email-feedback');
    
    if (isValidEmail(email)) {
        feedbackElement.textContent = 'Valid email address.';
        feedbackElement.style.color = 'green';
    } else {
        feedbackElement.textContent = 'Please enter a valid email address.';
        feedbackElement.style.color = 'red';
    }
}

// Function to update the UI for password validation feedback
function updatePasswordValidationUI() {
    const password = passwordInput.value;
    const feedbackElement = document.getElementById('password-feedback');
    
    if (isStrongPassword(password)) {
        feedbackElement.textContent = 'Strong password.';
        feedbackElement.style.color = 'green';
    } else {
        feedbackElement.textContent = 'Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.';
        feedbackElement.style.color = 'red';
    }
}

// Function to update the UI for confirm password validation feedback
function updateConfirmPasswordValidationUI() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const feedbackElement = document.getElementById('confirm-password-feedback');
    
    if (confirmPassword === password) {
        feedbackElement.textContent = 'Passwords match.';
        feedbackElement.style.color = 'green';
    } else {
        feedbackElement.textContent = 'Passwords do not match.';
        feedbackElement.style.color = 'red';
    }
}

// Handle Auth Form Submission
authForm.onsubmit = async function (event) {
    event.preventDefault();
    const username = usernameInput.value;
    const password = passwordInput.value;

    // Validate email format
    if (!isValidEmail(username)) {
        alert('Please enter a valid email address.');
        return; // Prevent submission if email is not valid
    }

    // Login Logic
    if (confirmPasswordGroup.style.display === 'none') {
        if (username && password) {
            try {
                const response = await fetch('/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: username, password: password }),
                });

                if (response.ok) {
                    // Show success alert
                    alert('Login Successful!.');
                    const data = await response.json();
                    const token = data.access_token;

                    // Store JWT token in localStorage
                    localStorage.setItem('jwt', token);

                    authModal.style.display = 'none'; 
                    fetchPersonalDetails(username); 
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail || response.statusText}`);
                }
            } catch (error) {
                console.error('Error during login:', error);
            }
        }
    } else {
        // Registration Logic
        const confirmPassword = confirmPasswordInput.value;
        if (password === confirmPassword) {
            if (!isStrongPassword(password)) {
                alert('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.');
                return; 
            }
            try {
                const response = await fetch('/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: username, password: password }),
                });

                if (response.ok) {
                    // Show success alert
                    alert('User registration successful! Please log in.');

                    // Switch back to login view
                    confirmPasswordGroup.style.display = 'none';
                    document.getElementById('modal-title').textContent = 'Login';
                    registerButton.textContent = 'Register';
                    location.reload();
                }
            } catch (error) {
                console.error('Error during registration:', error);
            }
        }   else {
            alert('Passwords do not match. Please try again.');
        }
    }
};

// Event listeners for real-time validation
usernameInput.addEventListener('input', updateEmailValidationUI);
passwordInput.addEventListener('input', updatePasswordValidationUI);
confirmPasswordInput.addEventListener('input', updateConfirmPasswordValidationUI);

// Handle Registration Button
registerButton.onclick = function () {
    if (confirmPasswordGroup.style.display === 'none') {
        // Switch to registration
        confirmPasswordGroup.style.display = 'block';
        document.getElementById('modal-title').textContent = 'Register';
        registerButton.textContent = 'Back to Login';
    } else {
        // Switch back to login
        confirmPasswordGroup.style.display = 'none';
        document.getElementById('modal-title').textContent = 'Login';
        registerButton.textContent = 'Register';
        
    }
};

// Handle Chat Form Submission
chatForm.onsubmit = function (event) {
    event.preventDefault();
    const message = messageInput.value.trim();
    
    if (message) {
        appendMessage('user', message);
        messageInput.value = ''; // Clear input field

        // Simulated response from the bot
        setTimeout(() => {
            appendMessage('bot', 'This is a simulated response.');
        }, 1000);
    }
};

// Function to append messages to the chat
function appendMessage(sender, text) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    messageElement.textContent = text;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
}

// Fetch Personal Details after Login
async function fetchPersonalDetails(email) {
    try {
        const response = await fetch(`/personal-details/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        });
        
        if (response.ok) {
            const personalDetails = await response.json();
            console.log('Personal Details:', personalDetails);
            // You can display the personal details in the UI as needed
        } else {
            console.error('Error fetching personal details:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching personal details:', error);
    }
}

// Logout logic


logoutButton.onclick = async function () {
    // Remove JWT from localStorage
    localStorage.removeItem('jwt');

    // Optionally, you can notify the backend about logout
    try {
        const response = await fetch('/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            alert('Logout successful.');
            location.reload();
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.detail || response.statusText}`);
        }
    } catch (error) {
        console.error('Error during logout:', error);
    }
};
