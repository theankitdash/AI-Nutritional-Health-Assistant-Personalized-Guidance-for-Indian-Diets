document.addEventListener('DOMContentLoaded', (event) => {
    const menuItems = document.querySelectorAll('.menu-items a');
    const sections = document.querySelectorAll('.section, .logout');

    // Function to show the selected section and hide others
    function showSection(targetId) {
        sections.forEach(section => {
            if (section.id === targetId) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    }

    // Set default section on page load
    showSection('profile');

    // Add click event listeners to menu items
    menuItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            const targetId = item.getAttribute('data-target');
            showSection(targetId);
        });
    });
});
