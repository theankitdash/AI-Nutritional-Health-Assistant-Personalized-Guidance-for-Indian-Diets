document.addEventListener("DOMContentLoaded", async () => {
    const saveProfileBtn = document.getElementById("saveProfileBtn");
    const changePasswordBtn = document.getElementById("changePasswordBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const submitChangePasswordBtn = document.getElementById("submitChangePasswordBtn");
    const closeModal = document.getElementById("closeModal");
    const changePasswordModal = document.getElementById("changePasswordModal");
    const feedbackElement = document.getElementById('password-feedback');

    // Fetch and display user personal details on load
    await fetchPersonalDetails();

    // Function to handle fetch requests
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

    // Event to save profile
    saveProfileBtn.addEventListener("click", async () => {
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
        } catch (error) {
            alert(`Error saving profile: ${error.message}`);
        }
    });

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

    // Real-time password strength feedback
    const newPasswordInput = document.getElementById("newPassword");
    newPasswordInput.addEventListener("input", () => {
        if (isStrongPassword(newPasswordInput.value)) {
            feedbackElement.textContent = 'Strong password.';
            feedbackElement.style.color = 'green';
        } else {
            feedbackElement.textContent = 'Weak password. Ensure it meets the requirements.';
            feedbackElement.style.color = 'red';
        }
    });

    // Event to open change password modal
    changePasswordBtn.addEventListener("click", () => {
        changePasswordModal.style.display = "block"; // Show modal
    });

    // Event to close change password modal
    closeModal.addEventListener("click", () => {
        changePasswordModal.style.display = "none"; // Hide modal
    });

    // Event to submit new password
    submitChangePasswordBtn.addEventListener("click", async () => {
        const currentPassword = document.getElementById("currentPassword").value;
        const newPassword = newPasswordInput.value;

        try {
            await fetchData("/update-password/", "PUT", { current_password: currentPassword, new_password: newPassword });
            alert("Password changed successfully!");
            changePasswordModal.classList.add("hidden"); // Close modal
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    });

    // Event to logout
    logoutBtn.addEventListener("click", async () => {
        try {
            await fetchData("/logout/", "POST");
            alert("Logged out successfully!");
            window.location.href = "/"; // Redirect to home page
        } catch (error) {
            alert(`Error logging out: ${error.message}`);
        }
    });

    // Function to fetch and display personal details
    async function fetchPersonalDetails() {
        try {
            const data = await fetchData("/personal-details/", "GET");
            document.getElementById("welcome-name").textContent = data.name; // Display the welcome name
            document.getElementById("name").value = data.name;
            document.getElementById("dateOfBirth").value = data.date_of_birth;
            document.getElementById("gender").value = data.gender;
            document.getElementById("height").value = data.height;
            document.getElementById("weight").value = data.weight;
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
});
