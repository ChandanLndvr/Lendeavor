document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.getElementById('delete-selected-button');
    const checkboxes = document.querySelectorAll('input[name="job_ids"]');
    const selectAll = document.getElementById('select-all');

    function toggleDeleteButton() {
        const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
        deleteBtn.style.display = anyChecked ? 'inline-block' : 'none';
    }

    // Toggle individual checkbox
    checkboxes.forEach(cb => cb.addEventListener('change', toggleDeleteButton));

    // Select all functionality
    selectAll.addEventListener('change', function () {
        const checked = this.checked;
        checkboxes.forEach(cb => cb.checked = checked);
        toggleDeleteButton();
    });

    // Initialize button visibility on page load
    toggleDeleteButton();
});
