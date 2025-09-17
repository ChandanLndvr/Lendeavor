document.addEventListener('DOMContentLoaded', function() {
    // Select the first <form> element on the page
    const form = document.querySelector('form');

    // Listen for form submission event
    form.addEventListener('submit', function(e) {
        // Get the value of the button that triggered the submit event
        // e.submitter is the button or input that triggered form submit (modern browsers)
        const action = e.submitter ? e.submitter.value : '';

        console.log('Form submitted, action:', action); // Debug log

        // Confirmation for single job update
        if (action === 'update') {
            if (!confirm("Are you sure you want to update this job or news?")) {
                // User clicked Cancel, prevent form submission
                e.preventDefault();
            }
        } 
        // Confirmation for single job delete
        else if (action === 'delete') {
            if (!confirm("Are you sure you want to delete this job or news? This action cannot be undone.")) {
                e.preventDefault();
            }
        }
        // Confirmation for bulk job deletion (multiple selected jobs)
        else if (action === 'delete_selected') {
            if (!confirm("Are you sure you want to delete the selected job(s) or news? This action cannot be undone.")) {
                e.preventDefault();
            }
        }
        // If no matching action, no confirmation needed
    });
});