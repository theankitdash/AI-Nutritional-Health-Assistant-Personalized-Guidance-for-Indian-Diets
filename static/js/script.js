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

// Handle Auth Form Submission
authForm.onsubmit = async function (event) {
    event.preventDefault();
    const username = usernameInput.value;
    const password = passwordInput.value;

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
                    console.log('Login successful');
                    authModal.style.display = 'none'; // Close modal on successful login
                    fetchPersonalDetails(username); // Fetch personal details after login
                } else {
                    alert('Invalid email or password');
                }
            } catch (error) {
                console.error('Error during login:', error);
            }
        } else {
            alert('Please enter both username and password.');
        }
    } else {
        // Registration Logic
        const confirmPassword = confirmPasswordInput.value;
        if (password === confirmPassword) {
            try {
                const response = await fetch('/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: username, password: password }),
                });

                if (response.ok) {
                    console.log('Registration successful');
                    // Switch back to login view
                    confirmPasswordGroup.style.display = 'none';
                    document.getElementById('modal-title').textContent = 'Login';
                    registerButton.textContent = 'Register';
                    alert('Registration successful! You can now log in.');
                } else {
                    alert('Error during registration');
                }
            } catch (error) {
                console.error('Error during registration:', error);
            }
        } else {
            alert('Passwords do not match.');
        }
    }
};

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
        const response = await fetch(`/personal-details/${email}`);
        
        if (response.ok) {
            const personalDetails = await response.json();
            console.log('Personal details:', personalDetails);

            // You can display the personal details in the UI as needed
            alert(`Welcome, ${personalDetails.name}!`);
        } else {
            console.log('Failed to fetch personal details');
        }
    } catch (error) {
        console.error('Error fetching personal details:', error);
    }
}
