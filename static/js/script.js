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

    // Chat History modal
    const chathistoryModal = document.getElementById('chat-history-modal');
    const chathistoryBtn = document.getElementById('chat-history-btn');
    const closechathistoryModal = document.getElementById('close-chat-history');

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
        const preferences = {
            foodPreference: document.querySelector('input[name="food-preference"]:checked')?.value,
            cuisinePreferences: Array.from(document.querySelectorAll('input[name="cuisine-preference"]:checked')).map(el => el.value),
            spicyFoodTolerance: document.querySelector('input[name="spicy-food-tolerance"]:checked')?.value,
            preferredMealType: document.querySelector('input[name="preferred-meal-type"]:checked')?.value,
            favoriteMeal: document.getElementById('favorite-meal')?.value,
            mealFrequency: document.getElementById('meal-frequency')?.value,
            hydrationLevel: document.getElementById('hydration-level')?.value,
            activityLevel: document.getElementById('activity-level')?.value,
            fitnessGoal: document.getElementById('fitness-goal')?.value,
            foodRestrictions: Array.from(document.querySelectorAll('input[name="food-restrictions"]:checked')).map(el => el.value),
            caffeineIntake: document.getElementById('caffeine-intake')?.value,
            averageSleep: document.getElementById('average-sleep')?.value,
            sleepQuality: document.getElementById('sleep-quality')?.value,
            supplementUsage: document.querySelector('input[name="supplement-usage"]:checked')?.value,
            supplementFrequency: document.getElementById('supplement-frequency')?.value,
            snackPreferences: Array.from(document.querySelectorAll('input[name="snack-preference"]:checked')).map(el => el.value),
            mealTimings: Array.from(document.querySelectorAll('input[name="meal-timings"]:checked')).map(el => el.value),
            cheatDayFrequency: document.getElementById('cheat-day-frequency')?.value,
            culturalPreferences: Array.from(document.querySelectorAll('input[name="cultural-preferences"]:checked')).map(el => el.value),
            preferredIngredients: Array.from(document.querySelectorAll('input[name="preferred-ingredients"]:checked')).map(el => el.value),
            sweetPreference: document.querySelector('input[name="sweet-preference"]:checked')?.value,
            eatingOutFrequency: document.getElementById('eating-out-frequency')?.value,
            preferredDrinks: Array.from(document.querySelectorAll('input[name="preferred-drinks"]:checked')).map(el => el.value)
        };

        if (preferences) {
            try {
            await fetchData('/preferences', "POST", preferences);

                alert("Preferences saved successfully!");
                preferencesModal.style.display = 'none';
            } catch (error) {
                alert("Error saving preferences:", error);
            }
        } else {
            alert("Please update all the preferences.");
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
        const healthConditions = {
            allergies: document.getElementById("allergies").value,
            diabetes: document.getElementById("diabetes").checked,
            hypertension: document.getElementById("hypertension").checked,
            cholesterol: document.getElementById("cholesterol").checked,
            thyroid: document.getElementById("thyroid").checked,
            kidneyDisease: document.getElementById("kidney-disease").checked,
            liverDisease: document.getElementById("liver-disease").checked,
            lactoseIntolerance: document.getElementById("lactose-intolerance").checked,
            glutensensitivity: document.getElementById("glutensensitivity").checked,
            pcos: document.getElementById("pcos").checked,
            anemia: document.getElementById("anemia").checked,
            osteoporosis: document.getElementById("osteoporosis").checked,
            ibs: document.getElementById("ibs").checked,
            gerd: document.getElementById("gerd").checked,
            gout: document.getElementById("gout").checked,
            otherConditions: document.getElementById("other-conditions").value
        };

        if (healthConditions) {
            try {
                await fetchData('/health-conditions', "POST", healthConditions);
                alert("Health conditions saved successfully!");
                healthConditionsModal.style.display = 'none';
            } catch (error) {
                alert("Error saving health conditions:", error);
            }
        } else {
            alert("Please update all the health conditions.");
        }
    });

    // Function to toggle PCOS field based on gender
    function togglePCOSField(gender) {
        const pcosField = document.getElementById("pcos-field");
        if (gender === "female") {
        pcosField.style.display = "block";
        } else {
        pcosField.style.display = "none";
        }
    }

    // Example: Call togglePCOSField() with user's gender when the modal opens
    document.addEventListener("DOMContentLoaded", function () {
        const userGender = document.getElementById('gender'); // Replace this with actual gender value from your database
        togglePCOSField(userGender);
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

            // Set the food preference
            document.querySelector(`input[name="food-preference"][value="${data.food_preference}"]`).checked = true;

            // Set cuisine preferences (multiple checkboxes)
            data.cuisine_preferences.split(',').forEach(value => 
                document.querySelector(`input[name="cuisine-preference"][value="${value}"]`).checked = true
            );

            // Set spicy food tolerance
            document.querySelector(`input[name="spicy-food-tolerance"][value="${data.spicy_food_tolerance}"]`).checked = true;

            // Set preferred meal type
            document.querySelector(`input[name="preferred-meal-type"][value="${data.preferred_meal_type}"]`).checked = true;

            // Set favorite meal
            document.getElementById('favorite-meal').value = data.favorite_meal;

            // Set meal frequency
            document.getElementById('meal-frequency').value = data.meal_frequency;

            // Set hydration level
            document.getElementById('hydration-level').value = data.hydration_level;

            // Set activity level
            document.getElementById('activity-level').value = data.activity_level;

            // Set fitness goal
            document.getElementById('fitness-goal').value = data.fitness_goal;

            // Set food restrictions (multiple checkboxes)
            data.food_restrictions.split(',').forEach(value => 
                document.querySelector(`input[name="food-restrictions"][value="${value}"]`).checked = true
            );

            // Set caffeine intake
            document.getElementById('caffeine-intake').value = data.caffeine_intake;

            // Set average sleep
            document.getElementById('average-sleep').value = data.average_sleep;

            // Set sleep quality
            document.getElementById('sleep-quality').value = data.sleep_quality;

            // Set supplement usage
            document.querySelector(`input[name="supplement-usage"][value="${data.supplement_usage}"]`).checked = true;

            // Set supplement frequency
            document.getElementById('supplement-frequency').value = data.supplement_frequency;

            // Set snack preferences (multiple checkboxes)
            data.snack_preferences.split(',').forEach(value => 
                document.querySelector(`input[name="snack-preference"][value="${value}"]`).checked = true
            );

            // Set meal timings (multiple checkboxes)
            data.meal_timings.split(',').forEach(value => 
                document.querySelector(`input[name="meal-timings"][value="${value}"]`).checked = true
            );

            // Set cheat day frequency
            document.getElementById('cheat-day-frequency').value = data.cheat_day_frequency;

            // Set cultural preferences (multiple checkboxes)
            data.cultural_preferences.split(',').forEach(value => 
                document.querySelector(`input[name="cultural-preferences"][value="${value}"]`).checked = true
            );

            // Set preferred ingredients (multiple checkboxes)
            data.preferred_ingredients.split(',').forEach(value => 
                document.querySelector(`input[name="preferred-ingredients"][value="${value}"]`).checked = true
            );

            // Set sweet preference
            document.querySelector(`input[name="sweet-preference"][value="${data.sweet_preference}"]`).checked = true;

            // Set eating out frequency
            document.getElementById('eating-out-frequency').value = data.eating_out_frequency;

            // Set preferred drinks (multiple checkboxes)
            data.preferred_drinks.split(',').forEach(value => 
                document.querySelector(`input[name="preferred-drinks"][value="${value}"]`).checked = true
            );

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
            document.getElementById("diabetes").checked = !!data.diabetes;
            document.getElementById("hypertension").checked = !!data.hypertension;
            document.getElementById("cholesterol").checked = !!data.cholesterol;
            document.getElementById("thyroid").checked = !!data.thyroid;
            document.getElementById("kidney-disease").checked = !!data.kidneyDisease;
            document.getElementById("liver-disease").checked = !!data.liverDisease;
            document.getElementById("lactose-intolerance").checked = !!data.lactoseIntolerance;
            document.getElementById("glutensensitivity").checked = !!data.glutensensitivity;
            document.getElementById("pcos").checked = !!data.pcos;
            document.getElementById("anemia").checked = !!data.anemia;
            document.getElementById("osteoporosis").checked = !!data.osteoporosis;
            document.getElementById("ibs").checked = !!data.ibs;
            document.getElementById("gerd").checked = !!data.gerd;
            document.getElementById("gout").checked = !!data.gout;
            // Set other conditions text
            document.getElementById("other-conditions").value = data.other_conditions || '';

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
                    appendMessage('bot', 'File analyzed successfully: ' + data.bot_response);
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
