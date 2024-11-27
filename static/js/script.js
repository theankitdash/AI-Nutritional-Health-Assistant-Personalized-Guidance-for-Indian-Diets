document.addEventListener("DOMContentLoaded", async () => {
    const authModal = document.getElementById('auth-modal');
    const closeModal = document.getElementById('close-auth-modal');
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
    const uploadButton = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');

    // Personal details modal and settings
    const personalDetailsModal = document.getElementById('personal-details-modal');
    const personalDetailsBtn = document.getElementById('personal-details-btn');
    const closePersonalDetailsModal = document.getElementById('close-personal-details');
    const savePersonalDetailsBtn = document.getElementById('save-personal-details');

    // Account settings modal and settings
    const accountSettingsModal = document.getElementById('account-settings-modal');
    const accountSettingsBtn = document.getElementById('account-settings-btn');
    const closeAccountSettingsModal = document.getElementById('close-account-settings');
    const changePasswordBtn = document.getElementById('change-password');
    const newPasswordInput = document.getElementById('newPassword');

    // Preferences modal
    const preferencesModal = document.getElementById('preferences-modal');
    const preferencesBtn = document.getElementById('preferences-btn');
    const closePreferencesModal = document.getElementById('close-preferences');
    const savePreferencesButton = document.getElementById('save-preferences');

    // Health conditions modal
    const healthConditionsModal = document.getElementById('health-conditions-modal');
    const healthConditionsBtn = document.getElementById('health-conditions-btn');
    const closeHealthConditionsModal = document.getElementById('close-health-conditions');
    const saveHealthConditionsButton = document.getElementById('save-health-conditions');

    // Check login status on page load
    window.onload = async () => {
        await checkLoginStatus();
    };

    // Check login status on page load
    async function checkLoginStatus() {
        // Check if the user is logged in using local storage
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        
        if (isLoggedIn) {
            const sessionExpiry = localStorage.getItem('sessionExpiry');
            const currentTime = new Date().getTime();

            // If session expiry exists and the current time is less than the expiry time, session is active
            if (sessionExpiry && currentTime < sessionExpiry) {
                // Session is active, proceed with fetching data
                fetchPersonalDetails(); 
                fetchPreferences();
                fetchHealthConditions();
            } else {
                // Reset local storage if the session is inactive
                localStorage.setItem('isLoggedIn', 'false');
                localStorage.removeItem('sessionExpiry');
                // Show the modal if session is expired
                authModal.style.display = 'block';
            }
        } else {
            // Show the modal if the user is not logged in
            authModal.style.display = 'block';
        } 
    }

    // Function to handle user login
    function handleLogin() {
        // Set the session expiration time (e.g., 1 hour from now)
        const expiryTime = new Date().getTime() + 3600000; // 1 hour

        // Store the login status and session expiry time in localStorage
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('sessionExpiry', expiryTime);

        // Close the authentication modal (if it's open)
        authModal.style.display = 'none';

        // Optionally, fetch user data immediately after login
        fetchPersonalDetails();
        fetchPreferences();
        fetchHealthConditions();
    }

    // Close modal when user clicks on <span> (x)
    closeModal.addEventListener('click', () => {
        authModal.style.display = 'none';
    });

    // Show preferences modal
    preferencesBtn.addEventListener('click', () => {
        preferencesModal.style.display = 'block';
    });

    // Close preferences modal
    closePreferencesModal.addEventListener('click', () => {
        preferencesModal.style.display = 'none';
    });
    

    // Save preferences
    savePreferencesButton.addEventListener('click', async () => {
        const selectedPreference = document.querySelector('input[name="food-preference"]:checked')?.value;

        if (selectedPreference) {
            try {
                await fetchData('/preferences', "POST", { diet_preference: selectedPreference });
                alert("Preferences saved successfully!");
                preferencesModal.style.display = 'none';
            } catch (error) {
                alert("Error saving preferences:", error);
            }
        } else {
            alert("Please select a food preference.");
        }
    });

    // Show health conditions modal
    healthConditionsBtn.addEventListener('click', () => {
        healthConditionsModal.style.display = 'block';
    });

    // Close health conditions modal
    closeHealthConditionsModal.addEventListener('click', () => {
        healthConditionsModal.style.display = 'none';
    });

    // Save health conditions
    saveHealthConditionsButton.addEventListener('click', async () => {
        const allergies = document.getElementById("allergies").value;

        if (allergies) {
            try {
                await fetchData('/health-conditions', "POST", { allergies });
                alert("Health conditions saved successfully!");
                healthConditionsModal.style.display = 'none';
            } catch (error) {
                alert("Error saving health conditions:", error);
            }
        } else {
            alert("Please enter your allergies.");
        }
    });

     // Event to show personal details modal
     personalDetailsBtn.addEventListener('click', () => {
        personalDetailsModal.style.display = 'block';
    });

    // Event to close personal details modal
    closePersonalDetailsModal.addEventListener('click', () => {
        personalDetailsModal.style.display = 'none';
    });

    // Event to save personal details
    savePersonalDetailsBtn.addEventListener('click', async () => {
        const name = document.getElementById("name").value;
        const dateOfBirth = document.getElementById("dateOfBirth").value;
        const gender = document.getElementById("gender").value;
        const height = parseFloat(document.getElementById("height").value);
        const weight = parseFloat(document.getElementById("weight").value);

        if (!name || !dateOfBirth || !gender || isNaN(height) || height <= 0 || isNaN(weight) || weight <= 0) {
            alert("Please fill all fields correctly.");
            return;
        }

        try {
            await fetchData("/personal-details/", "POST", { name, date_of_birth: dateOfBirth, gender, height, weight });
            alert("Profile saved successfully!");
            personalDetailsModal.style.display = 'none';
        } catch (error) {
            alert(`Error saving profile: ${error.message}`);
        }
    });

    // Event to show account settings modal
    accountSettingsBtn.addEventListener('click', () => {
        accountSettingsModal.style.display = 'block';
    });

    // Event to close account settings modal
    closeAccountSettingsModal.addEventListener('click', () => {
        accountSettingsModal.style.display = 'none';
    });

    const feedbackElement = document.getElementById('new-password-feedback');
    newPasswordInput.addEventListener("input", () => {
        if (isStrongPassword(newPasswordInput.value)) {
            feedbackElement.textContent = 'Strong password.';
            feedbackElement.style.color = 'green';
        } else {
            feedbackElement.textContent = 'Weak password. Ensure it meets the requirements.';
            feedbackElement.style.color = 'red';
        }
    });

    // Event to change password
    changePasswordBtn.addEventListener('click', async () => {
        const currentPassword = document.getElementById("currentPassword").value;
        const newPassword = newPasswordInput.value;

        if (isStrongPassword(newPassword)) {
            try {
                await fetchData("/update-password/", "PUT", { current_password: currentPassword, new_password: newPassword });
                alert("Password changed successfully!");
                accountSettingsModal.style.display = 'none';
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        } else {
            alert("Password does not meet the required strength.");
        }
    });

    // Function to fetch personal details
    async function fetchPersonalDetails() {
        try {
            const data = await fetchData("/personal-details/", "GET");
            console.log("Fetched Personal Details:", data);
            document.getElementById("welcome-name").textContent = data.name;
            document.getElementById("name").value = data.name;
            document.getElementById("dateOfBirth").value = data.date_of_birth;
            document.getElementById("gender").value = data.gender;
            document.getElementById("height").value = data.height;
            document.getElementById("weight").value = data.weight;
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    // Function to fetch preferences
    async function fetchPreferences() {
        try {
            const data = await fetchData("/preferences", "GET");
            console.log("Fetched Preferences:", data);
            // Set the food preference on the modal
            if (data.diet_preference) {
                document.querySelector(`input[name="food-preference"][value="${data.diet_preference}"]`).checked = true;
            }
        } catch (error) {
            alert(`Error fetching preferences: ${error.message}`);
        }
    }

    // Function to fetch health conditions
    async function fetchHealthConditions() {
        try {
            const data = await fetchData("/health-conditions", "GET");
            console.log("Fetched Health Conditions:", data);
            // Set allergies data
            document.getElementById("allergies").value = data.allergies || '';
        } catch (error) {
            alert(`Error fetching health conditions: ${error.message}`);
        }
    }

    // Fetch data helper function
    async function fetchData(url, method, body = null) {
        const options = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        return response.json();
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

    // Function to enable/disable real-time validation feedback
    function toggleValidationFeedback(isRegistration) {
        if (isRegistration) {
            // Enable validation feedback for registration
            usernameInput.addEventListener('input', updateEmailValidationUI);
            passwordInput.addEventListener('input', updatePasswordValidationUI);
            confirmPasswordInput.addEventListener('input', updateConfirmPasswordValidationUI);
        } else {
            // Disable validation feedback for login
            usernameInput.removeEventListener('input', updateEmailValidationUI);
            passwordInput.removeEventListener('input', updatePasswordValidationUI);
            confirmPasswordInput.removeEventListener('input', updateConfirmPasswordValidationUI);
        }
    }

    // Handle Auth Form Submission
    authForm.onsubmit = async function (event) {
        event.preventDefault();
        const username = usernameInput.value;
        const password = passwordInput.value;

        // Check if we are in the login process (when confirmPasswordGroup is hidden)
        const isLogin = confirmPasswordGroup.style.display === 'none';

        if (isLogin) {
            // Disable validation feedback for login
            toggleValidationFeedback(false);

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
                        handleLogin();
                        authModal.style.display = 'none'; 
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
                        alert('User registration successful! Please add personal details.');
                        authModal.style.display = 'none';
                        personalDetailsModal.style.display = 'block';
                    }
                } catch (error) {
                    console.error('Error during registration:', error);
                }
            } else {
                alert('Passwords do not match. Please try again.');
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

            // Clear fields and validation messages
            usernameInput.value = '';
            passwordInput.value = '';
            confirmPasswordInput.value = '';
            updateEmailValidationUI();
            updatePasswordValidationUI();
            updateConfirmPasswordValidationUI();

            // Enable validation feedback for registration
            toggleValidationFeedback(true);
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

            // Disable validation feedback for login
            toggleValidationFeedback(false);
        }
    };

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
                localStorage.removeItem('sessionExpiry');
                window.location.reload();
            } else {
                console.error('Error during logout:', response.statusText);
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    };

    // Handle Chat Form Submission
    chatForm.onsubmit = async function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        
        if (message) {
            appendMessage('user', message);
            messageInput.value = ''; // Clear input field

            // Call the backend to get the bot's response
            try {
                const response = await fetch('/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include', // Include cookies for session management
                    body: JSON.stringify({ message: message }), // Send the user message
                });

                if (response.ok) {
                    const data = await response.json();
                    appendMessage('bot', data.bot_response); // Display the bot's response
                } else {
                    appendMessage('bot', 'Error: Failed to get a response from the server.');
                }
            } catch (error) {
                appendMessage('bot', 'Error: Unable to connect to the server.');
            }
        }
    };
    
    // Function to append messages to the chat
    function appendMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${sender}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;

        messageElement.appendChild(messageContent);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
    }

    // Show file input when upload button is clicked
    uploadButton.onclick = () => {
        fileInput.click(); // Trigger file input click
    };

    // Handle file upload
    fileInput.onchange = async function () {
        const file = fileInput.files[0]; // Get the uploaded file
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/upload/', {
                    method: 'POST',
                    body: formData,
                    credentials: 'include', // Include cookies for session management
                });

                if (response.ok) {
                    const data = await response.json();
                    appendMessage('bot', 'File uploaded successfully: ' + data.filename);
                } else {
                    console.error('Error:', response.statusText);
                    appendMessage('bot', 'Error uploading file.');
                }
            } catch (error) {
                console.error('Error:', error);
                appendMessage('bot', 'Error communicating with the server.');
            }
        }
    };
});
