document.addEventListener("DOMContentLoaded", async () => {
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

    // Check login status on page load
    window.onload = checkLoginStatus;
    
    // Check login status on page load
    async function checkLoginStatus() {
        // Check if the user is logged in using local storage
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        
        if (isLoggedIn) {
            // Verify the session is still active with the server
            const isSessionActive = await isUserLoggedIn();

            if (isSessionActive) {
                // If the session is active, fetch personal details
                fetchPersonalDetails();
                return; // Exit the function to avoid showing the modal
            } else {
                // Reset local storage if the session is inactive
                localStorage.setItem('isLoggedIn', 'false');
            }
        }
        
        // Show the modal if the user is not logged in
        authModal.style.display = 'block';
    }

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

    // Function to check if the user is logged in
    async function isUserLoggedIn() {
        try {
            const response = await fetch(`/personal-details/`, { method: 'GET', credentials: 'include' });
            return response.ok; // Return true if logged in, false otherwise
        } catch (error) {
            alert('Error checking login status:', error);
            return false; // If error occurs, assume user is not logged in
        }
    }

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
                        alert('Login Successful!'); 
                        authModal.style.display = 'none'; 
                        localStorage.setItem('isLoggedIn', 'true'); // Set localStorage flag
                        fetchPersonalDetails(); // Fetch personal details after login
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
                        alert('User registration successful! Please add personal details.');
                        window.location.href = '/account-settings';
                    }
                } catch (error) {
                    console.error('Error during registration:', error);
                }
            } else {
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

            // Clear fields and validation messages
            usernameInput.value = '';
            passwordInput.value = '';
            confirmPasswordInput.value = '';
            updateEmailValidationUI();
            updatePasswordValidationUI();
            updateConfirmPasswordValidationUI();
        } else {
            // Switch back to login
            confirmPasswordGroup.style.display = 'none';
            document.getElementById('modal-title').textContent = 'Login';
            registerButton.textContent = 'Register';

            // Clear fields and validation messages
            usernameInput.value = '';
            passwordInput.value = '';
            confirmPasswordInput.value = '';
            updateEmailValidationUI();
            updatePasswordValidationUI();
            updateConfirmPasswordValidationUI();
        }
    };

    // Fetch Personal Details after Login
    async function fetchPersonalDetails() {
        
        try {
            const response = await fetch(`/personal-details/`, {
                method: 'GET',
                credentials: 'include', // Include cookies with the request
            });
            
            if (response.ok) {
                const personalDetails = await response.json();
                document.getElementById("welcome-name").textContent = personalDetails.name;
                return true;

            } else {
                alert('Error fetching personal details:', response.statusText);
                return false;
            }
        } catch (error) {
            alert('Error during fetch personal details:', error);
            return false;
        }
    }

    // Handle Logout
    logoutButton.onclick = async function () {
        try {
            const response = await fetch('/logout/', {
                method: 'POST',
                credentials: 'include', // Include cookies with the request
            });

            if (response.ok) {
                alert('Logout successful.');
                localStorage.setItem('isLoggedIn', 'false');
                window.location.reload();
            } else {
                console.error('Error during logout:', response.statusText);
            }
        } catch (error) {
            console.error('Error during logout:', error);
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
});
