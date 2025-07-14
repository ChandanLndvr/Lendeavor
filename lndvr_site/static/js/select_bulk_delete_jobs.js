document.addEventListener('DOMContentLoaded', function () {
    // Get the "Delete Selected" button
    const deleteBtn = document.getElementById('delete-selected-button');

    // Get all individual job selection checkboxes (name="job_ids")
    const checkboxes = document.querySelectorAll('input[name="job_ids"]');

    // Get the "Select All" checkbox
    const selectAll = document.getElementById('select-all');

    // Function to toggle visibility of the "Delete Selected" button
    function toggleDeleteButton() {
        // Check if any job checkbox is checked
        const anyChecked = Array.from(checkboxes).some(cb => cb.checked);

        // Show the delete button if any job is selected; otherwise hide it
        deleteBtn.style.display = anyChecked ? 'inline-block' : 'none';
    }

    // Add event listeners on individual job checkboxes to update delete button visibility
    checkboxes.forEach(cb => cb.addEventListener('change', toggleDeleteButton));

    // Add event listener on the "Select All" checkbox to toggle all individual checkboxes
    selectAll.addEventListener('change', function () {
        const checked = this.checked;

        // Set all individual checkboxes to the same state as "Select All"
        checkboxes.forEach(cb => cb.checked = checked);

        // Update delete button visibility
        toggleDeleteButton();
    });

    // Initialize delete button visibility on page load
    toggleDeleteButton();
});