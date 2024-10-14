// Fetch personal details on page load
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("jwt");
    if (token) {
        try {
            const response = await fetch("/personal-details/", {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                // Populate the fields with fetched data
                document.getElementById("name").value = data.name || ""; // Populate name field
                document.getElementById("dateOfBirth").value = data.date_of_birth || ""; // Populate date of birth
                document.getElementById("gender").value = data.gender || "other"; // Populate gender
                document.getElementById("height").value = data.height || ""; // Populate height
                document.getElementById("weight").value = data.weight || ""; // Populate weight
                document.getElementById("welcome-name").textContent = data.name; // Update welcome message
            } else {
                const errorData = await response.json();
                console.error("Failed to fetch personal details:", errorData.detail);
            }
        } catch (error) {
            console.error("Error fetching personal details:", error);
        }
    } else {
        console.log("No access token found.");
    }
});

// Update personal details
document.getElementById("saveProfileBtn").addEventListener("click", async () => {
    const token = localStorage.getItem("jwt");
    if (token) {
        const updatedDetails = {
            name: document.getElementById("name").value,
            date_of_birth: document.getElementById("dateOfBirth").value,
            gender: document.getElementById("gender").value,
            height: parseFloat(document.getElementById("height").value),
            weight: parseFloat(document.getElementById("weight").value)
            
        };

        try {
            const response = await fetch("/personal-details/", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(updatedDetails)
            });

            if (response.ok) {
                const result = await response.json();
                alert(result.message); // Success message
            } else {
                const errorData = await response.json();
                console.error("Failed to update personal details:", errorData.detail);
                alert("Failed to update personal details: " + errorData.detail);
            }
        } catch (error) {
            console.error("Error updating personal details:", error);
            alert("An error occurred while updating personal details.");
        }
    } else {
        alert("You must be logged in to update your personal details.");
    }
});

// Show the password change modal
function showModal() {
    document.getElementById("changePasswordModal").style.display = "block";
}

// Hide the password change modal
function hideModal() {
    document.getElementById("changePasswordModal").style.display = "none";
}

// Show the modal when the change password button is clicked
document.getElementById("changePasswordBtn").addEventListener("click", showModal);

// Hide the modal when the close button is clicked
document.getElementById("closeModal").addEventListener("click", hideModal);

// Hide the modal when clicking outside of the modal content
window.addEventListener("click", (event) => {
    const modal = document.getElementById("changePasswordModal");
    if (event.target === modal) {
        hideModal();
    }
});

// Submit the password change
document.getElementById("submitChangePasswordBtn").addEventListener("click", async () => {
    const token = localStorage.getItem("jwt");
    if (token) {
        const passwordData = {
            current_password: document.getElementById("currentPassword").value,
            new_password: document.getElementById("newPassword").value
        };

        try {
            const response = await fetch("/update-password/", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(passwordData)
            });

            if (response.ok) {
                const result = await response.json();
                alert(result.message); // Success message
                hideModal(); // Hide the modal after successful update
            } else {
                const errorData = await response.json();
                console.error("Failed to update password:", errorData.detail);
                alert("Failed to update password: " + errorData.detail);
            }
        } catch (error) {
            console.error("Error updating password:", error);
            alert("An error occurred while updating the password.");
        }
    } else {
        alert("You must be logged in to update your password.");
    }
});

// Logout functionality
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("jwt");
    alert("Logged out successfully.");
    window.location.href = "/";
});
