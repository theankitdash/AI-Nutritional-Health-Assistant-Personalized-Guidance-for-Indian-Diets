// Fetch personal details on page load
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("accessToken");
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
                document.getElementById("name").textContent = data.name;
                document.getElementById("name").value = data.name;
                document.getElementById("gender").value = data.gender;
                document.getElementById("height").value = data.height;
                document.getElementById("weight").value = data.weight;
                document.getElementById("dateOfBirth").value = data.date_of_birth;
            } else {
                console.error("Failed to fetch personal details:", response.statusText);
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
    const token = localStorage.getItem("accessToken");
    if (token) {
        const updatedDetails = {
            name: document.getElementById("name").value,
            gender: document.getElementById("gender").value,
            height: parseFloat(document.getElementById("height").value),
            weight: parseFloat(document.getElementById("weight").value),
            date_of_birth: document.getElementById("dateOfBirth").value
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
                alert(result.message);
            } else {
                console.error("Failed to update personal details:", response.statusText);
                alert("Failed to update personal details.");
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
document.getElementById("changePasswordModalBtn").addEventListener("click", showModal);

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
    const token = localStorage.getItem("accessToken");
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
                alert(result.message);
                // Hide the modal after successful update
                hideModal();
            } else {
                console.error("Failed to update password:", response.statusText);
                alert("Failed to update password.");
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
    localStorage.removeItem("accessToken");
    alert("Logged out successfully.");
    window.location.href = "/";
});
