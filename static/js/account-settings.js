document.addEventListener("DOMContentLoaded", async () => {
    const saveProfileBtn = document.getElementById("saveProfileBtn");
    const changePasswordBtn = document.getElementById("changePasswordBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const submitChangePasswordBtn = document.getElementById("submitChangePasswordBtn");
    const closeModal = document.getElementById("closeModal");
    const changePasswordModal = document.getElementById("changePasswordModal");

    // Fetch and display user personal details on load
    await fetchPersonalDetails();

    // Event to save profile
    saveProfileBtn.addEventListener("click", async () => {
        const name = document.getElementById("name").value;
        const dateOfBirth = document.getElementById("dateOfBirth").value;
        const gender = document.getElementById("gender").value;
        const height = parseFloat(document.getElementById("height").value);
        const weight = parseFloat(document.getElementById("weight").value);

        const response = await fetch("/personal-details/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, date_of_birth: dateOfBirth, gender, height, weight }),
        });

        if (response.ok) {
            alert("Profile saved successfully!");
        } else {
            const error = await response.json();
            alert(`Error saving profile: ${error.detail}`);
        }
    });

    // Event to open change password modal
    changePasswordBtn.addEventListener("click", () => {
        changePasswordModal.style.display = "block";
    });

    // Event to close change password modal
    closeModal.addEventListener("click", () => {
        changePasswordModal.style.display = "none";
    });

    // Event to submit new password
    submitChangePasswordBtn.addEventListener("click", async () => {
        const currentPassword = document.getElementById("currentPassword").value;
        const newPassword = document.getElementById("newPassword").value;

        const response = await fetch("/update-password/", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
        });

        if (response.ok) {
            alert("Password changed successfully!");
            changePasswordModal.style.display = "none"; // Close modal
        } else {
            const error = await response.json();
            alert(`Error changing password: ${error.detail}`);
        }
    });

    // Event to logout
    logoutBtn.addEventListener("click", async () => {
        const response = await fetch("/logout/", {
            method: "POST",
            credentials: "include", // Ensure cookies are sent
        });

        if (response.ok) {
            alert("Logged out successfully!");
            window.location.href = "/"; // Redirect to home page
        } else {
            const error = await response.json();
            alert(`Error logging out: ${error.detail}`);
        }
    });

    // Function to fetch and display personal details
    async function fetchPersonalDetails() {
        const sessionId = getCookie('session_id');
        if (!sessionId) {
            console.error('User not logged in. Session ID missing.');
            return;
        }
        try {
            const response = await fetch("/personal-details/", {
                method: "GET",
                credentials: "include", // Ensure cookies are sent
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById("welcome-name").textContent = data.name; // Display the welcome name
                document.getElementById("name").value = data.name;
                document.getElementById("dateOfBirth").value = data.date_of_birth;
                document.getElementById("gender").value = data.gender;
                document.getElementById("height").value = data.height;
                document.getElementById("weight").value = data.weight;
            } else {
                alert("Error fetching personal details. Please log in again.");
                window.location.href = "/"; // Redirect to home page if there's an error
            }
        } catch (error) {
            console.error('Error fetching personal details:', error);
        }
    }
});
